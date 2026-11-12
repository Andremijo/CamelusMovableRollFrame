"""Runs CamelusMovableRollFrame.lua in real Lua 5.1 with small stand-in frames.

The stand-ins copy what WoW Forever's default UI does with the roll window
(Blizzard_UIPanels_Game/Mainline/GroupLootFrame.lua and the managed frame layout):
GroupLootContainer gets ClearAllPoints + SetPoint whenever it is shown or laid out.

Usage: pip install lupa && python3 tests/test_addon.py
"""
import os
import sys

from lupa import lua51

HERE = os.path.dirname(os.path.abspath(__file__))
ADDON = os.path.join(HERE, "..", "CamelusMovableRollFrame.lua")

MOCKS = r"""
local Frame = {}
Frame.__index = Frame

function Frame:SetSize(w, h) self.w, self.h = w, h end
function Frame:GetWidth() return self.w or 0 end
function Frame:GetHeight() return self.h or 0 end
function Frame:SetFrameStrata() end
function Frame:SetMovable(v) self.movable = v end
function Frame:SetClampedToScreen() end
function Frame:EnableMouse(v) self.mouse = v end
function Frame:ClearAllPoints() self.points = {} end
function Frame:SetPoint(...) self.points = self.points or {}; table.insert(self.points, {...}) end
function Frame:GetPoint() local p = self.points[1]; return p[1], p[2], p[3], p[4], p[5] end
function Frame:SetScale(s) self.scale = s end
-- Newer clients switch mouse input on when a mouse script is set, so the
-- stand-in does the same. A frame that has it on and is shown catches clicks.
local MOUSE_SCRIPTS = { OnMouseDown = true, OnMouseUp = true, OnEnter = true, OnLeave = true, OnClick = true }
function Frame:SetScript(name, fn)
    self.scripts[name] = fn
    if fn and MOUSE_SCRIPTS[name] then self.mouse = true end
end
function Frame:HookScript(name, fn)
    local old = self.scripts[name]
    self.scripts[name] = function(...) if old then old(...) end fn(...) end
    if MOUSE_SCRIPTS[name] then self.mouse = true end
end
function Frame:SetAllPoints() end
function Frame:IsVisible()
    local f = self
    while f do
        if f.shown == false then return false end
        f = f.parent
    end
    return true
end
function Frame:RegisterEvent(e) self.events[e] = true end
function Frame:UnregisterEvent(e) self.events[e] = nil end
function Frame:StartMoving() self.moving = true end
function Frame:StopMovingOrSizing()
    self.moving = false
    -- the game converts a dragged frame's anchor like this
    self.points = { { "BOTTOMLEFT", UIParent, "BOTTOMLEFT", 600, 420 } }
end
function Frame:SetUserPlaced() end
function Frame:Show() self.shown = true; if self.scripts.OnShow then self.scripts.OnShow(self) end end
function Frame:Hide()
    local was = self.shown ~= false
    self.shown = false
    if was and self.scripts.OnHide then self.scripts.OnHide(self) end
end
function Frame:CreateTexture()
    return { SetAllPoints = function() end, SetColorTexture = function() end,
             Show = function(t) t.shown = true end, Hide = function(t) t.shown = false end }
end
function Frame:CreateFontString()
    return { SetPoint = function() end, SetText = function() end,
             Show = function() end, Hide = function() end }
end

local function NewFrame(name, parent)
    local f = setmetatable({ scripts = {}, events = {}, points = {}, children = {}, name = name, parent = parent }, Frame)
    if name then _G[name] = f end
    if parent then table.insert(parent.children, f) end
    return f
end

function CreateFrame(_, name, parent) return NewFrame(name, parent) end

-- True if a frame from the addon is shown and would catch a click.
function AddonCatchesClicks()
    local function walk(f)
        if f.mouse and f:IsVisible() then return true end
        for _, c in ipairs(f.children) do if walk(c) then return true end end
        return false
    end
    return walk(CamelusMovableRollFrameAnchor)
end

-- WoW's hooksecurefunc(table, "method", fn): call the original, then fn.
function hooksecurefunc(t, method, fn)
    local orig = t[method]
    t[method] = function(...) local r = { orig(...) }; fn(...); return unpack(r) end
end

UIParent = NewFrame("UIParent")
messages = {}
DEFAULT_CHAT_FRAME = { AddMessage = function(_, m) table.insert(messages, m) end }
shiftDown = false
function IsShiftKeyDown() return shiftDown end

SlashCmdList = {}

GroupLootContainer = NewFrame("GroupLootContainer")
GroupLootContainer.reservedSize = 100
GroupLootContainer:SetSize(256, 1)
for i = 1, 4 do NewFrame("GroupLootFrame" .. i):SetSize(277, 67) end

-- What the managed frame layout does when the container is shown / laid out.
function BlizzardLayout()
    GroupLootContainer:ClearAllPoints()
    GroupLootContainer:SetPoint("BOTTOM", BottomManagedFrameContainer, "BOTTOM", 0, 123)
end
BottomManagedFrameContainer = NewFrame("BottomManagedFrameContainer")

function FireEvent(event, ...)
    local a = CamelusMovableRollFrameAnchor
    if a.events[event] then a.scripts.OnEvent(a, event, ...) end
end
"""

failures = 0


def check(name, ok):
    global failures
    print(("PASS " if ok else "FAIL ") + name)
    if not ok:
        failures += 1


def new_lua():
    lua = lua51.LuaRuntime(unpack_returned_tuples=True)
    lua.execute(MOCKS)
    with open(ADDON, encoding="utf-8") as f:
        lua.execute(f.read())
    return lua


lua = new_lua()
g = lua.globals()
anchor = g.CamelusMovableRollFrameAnchor
container = g.GroupLootContainer

lua.execute('FireEvent("ADDON_LOADED", "SomeOtherAddon")')
check("ignores other addons' ADDON_LOADED", g.CamelusMovableRollFrameDB is None)

lua.execute('FireEvent("ADDON_LOADED", "CamelusMovableRollFrame")')
db = g.CamelusMovableRollFrameDB
check("saved variables get defaults", db.point == "BOTTOM" and db.y == 200 and db.scale == 1)

lua.execute('FireEvent("PLAYER_LOGIN")')
check("locked after login: nothing from the addon catches clicks", lua.eval("AddonCatchesClicks()") is False)
check("anchor placed at saved spot",
      lua.eval('CamelusMovableRollFrameAnchor.points[1][1] == "BOTTOM" and CamelusMovableRollFrameAnchor.points[1][5] == 200'))
check("anchor sized like roll frame and its slot", anchor.w == 277 and anchor.h == 100)
check("container pinned to anchor at login",
      lua.eval('#GroupLootContainer.points == 1 and GroupLootContainer.points[1][2] == CamelusMovableRollFrameAnchor'))

lua.execute("BlizzardLayout()")
check("container pinned again after Blizzard's layout moves it",
      lua.eval('#GroupLootContainer.points == 1 and GroupLootContainer.points[1][2] == CamelusMovableRollFrameAnchor'))

# Shift + drag on a roll window moves the anchor and saves the spot.
lua.execute('shiftDown = true; GroupLootFrame2.scripts.OnMouseDown(GroupLootFrame2, "LeftButton")')
check("shift + drag starts moving the anchor", anchor.moving is True)
lua.execute('GroupLootFrame2.scripts.OnMouseUp(GroupLootFrame2, "LeftButton"); shiftDown = false')
check("drop saves the new spot", db.point == "BOTTOMLEFT" and db.x == 600 and db.y == 420)

lua.execute('GroupLootFrame1.scripts.OnMouseDown(GroupLootFrame1, "LeftButton")')
check("plain click (no shift, locked) does not drag", anchor.moving is False)

# Scale: every roll frame and the container, anchor resized not scaled.
lua.execute('SlashCmdList.CAMELUSMOVABLEROLLFRAME("scale 1.5")')
check("scale applied to all four roll frames",
      lua.eval('GroupLootFrame1.scale == 1.5 and GroupLootFrame4.scale == 1.5'))
check("scale applied to the container", container.scale == 1.5)
check("anchor resized, keeps its spot",
      anchor.w == 277 * 1.5 and anchor.h == 150 and anchor.scale is None and db.x == 600)
lua.execute('SlashCmdList.CAMELUSMOVABLEROLLFRAME("scale 5")')
check("out-of-range scale refused", db.scale == 1.5)

# Unlock / lock with the drag box.
check("the anchor itself has no mouse scripts", anchor.scripts.OnMouseDown is None and anchor.mouse is None)
lua.execute('SlashCmdList.CAMELUSMOVABLEROLLFRAME("")')
check("/rollmove unlocks (blue box shown and takes the mouse)", lua.eval("AddonCatchesClicks()") is True)
lua.execute('local m = CamelusMovableRollFrameAnchor.children[1]; m.scripts.OnMouseDown(m, "LeftButton")')
check("unlocked box can be dragged without shift", anchor.moving is True)
lua.execute('SlashCmdList.CAMELUSMOVABLEROLLFRAME("")')
check("/rollmove again locks and finishes the drag", anchor.moving is False)
check("locked again: nothing from the addon catches clicks", lua.eval("AddonCatchesClicks()") is False)

lua.execute('SlashCmdList.CAMELUSMOVABLEROLLFRAME("reset")')
check("reset restores spot and size",
      db.point == "BOTTOM" and db.x == 0 and db.y == 200 and db.scale == 1
      and lua.eval("GroupLootFrame3.scale") == 1)

check("chat messages carry the addon name",
      all("Camelus' Movable Roll Frame" in m for m in lua.eval("messages").values()))

print()
print("all tests passed" if failures == 0 else f"{failures} test(s) failed")
sys.exit(1 if failures else 0)
