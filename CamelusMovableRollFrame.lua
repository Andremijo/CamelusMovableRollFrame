-- Camelus' Movable Roll Frame
-- Makes the Need / Greed / Pass roll window movable. Written for WoW Forever.
--
--   Shift + left-drag on a roll window   -> move it while a roll is up
--   /rollmove                            -> show/hide a drag handle (works with no roll up)
--   /rollmove reset                      -> back to the default spot and size
--   /rollmove scale 1.2                  -> make the roll windows bigger/smaller (0.5 - 2)
--
-- How the default UI works (WoW Forever, Blizzard_UIPanels_Game/Mainline/GroupLootFrame):
-- GroupLootFrame1-4 are children of UIParent. GroupLootContainer stacks them, each one
-- centred at container BOTTOM + reservedSize * (i - 0.5). The container itself is
-- placed by BottomManagedFrameContainer (a layout frame) every time it is shown.
-- We pin the container to our own anchor again after every SetPoint, and scale the
-- roll frames themselves (they are not children of the container, so scaling the
-- container alone would not scale them).
--
-- Taint: no fields are written on Blizzard frames, and no Blizzard function is replaced.

local ADDON_NAME = "CamelusMovableRollFrame"
local DEFAULTS = { point = "BOTTOM", relPoint = "BOTTOM", x = 0, y = 200, scale = 1 }
local NUM_ROLL_FRAMES = 4

local db
local unlocked = false
local applying = false
local baseWidth, baseHeight = 277, 100

local function Print(msg)
    DEFAULT_CHAT_FRAME:AddMessage("|cff33ccffCamelus' Movable Roll Frame|r: " .. msg)
end

-- Our own anchor. The roll window is pinned to it, and the player moves the anchor.
local anchor = CreateFrame("Frame", "CamelusMovableRollFrameAnchor", UIParent)
anchor:SetSize(baseWidth, baseHeight)
anchor:SetFrameStrata("DIALOG")
anchor:SetMovable(true)
anchor:SetClampedToScreen(true)
anchor:EnableMouse(false)

local overlay = anchor:CreateTexture(nil, "OVERLAY")
overlay:SetAllPoints(anchor)
overlay:SetColorTexture(0, 0.6, 1, 0.4)
overlay:Hide()

local label = anchor:CreateFontString(nil, "OVERLAY", "GameFontNormal")
label:SetPoint("CENTER", anchor, "CENTER", 0, 0)
label:SetText("Roll window\nDrag me, then type /rollmove to lock")
label:Hide()

-- WoW Forever stacks the roll windows in GroupLootContainer. Older clients have
-- no container and stack GroupLootFrame2-4 on GroupLootFrame1.
local function GetTarget()
    return GroupLootContainer or GroupLootFrame1
end

local function ForEachRollFrame(fn)
    for i = 1, NUM_ROLL_FRAMES do
        local frame = _G["GroupLootFrame" .. i]
        if frame then fn(frame) end
    end
end

local function PlaceAnchor()
    anchor:ClearAllPoints()
    anchor:SetPoint(db.point, UIParent, db.relPoint, db.x, db.y)
    -- The anchor is sized, not scaled, so its saved position stays put when the scale changes.
    anchor:SetSize(baseWidth * db.scale, baseHeight * db.scale)
end

local function AttachTarget()
    local target = GetTarget()
    if not target or applying then return end
    applying = true
    target:ClearAllPoints()
    target:SetPoint("BOTTOM", anchor, "BOTTOM", 0, 0)
    applying = false
end

local function ApplyScale()
    ForEachRollFrame(function(frame) frame:SetScale(db.scale) end)
    -- Scale the container too, so its height (which the loot toasts stack on) matches.
    if GroupLootContainer then GroupLootContainer:SetScale(db.scale) end
end

local function SavePosition()
    local point, _, relPoint, x, y = anchor:GetPoint()
    db.point, db.relPoint, db.x, db.y = point, relPoint, x, y
end

local function StartDrag(self, button)
    if button == "LeftButton" and (unlocked or IsShiftKeyDown()) then
        anchor:StartMoving()
        anchor.isDragging = true
    end
end

local function StopDrag()
    if anchor.isDragging then
        anchor:StopMovingOrSizing()
        anchor:SetUserPlaced(false)
        anchor.isDragging = nil
        SavePosition()
        AttachTarget()
    end
end

anchor:SetScript("OnMouseDown", StartDrag)
anchor:SetScript("OnMouseUp", StopDrag)
anchor:SetScript("OnHide", StopDrag)

local function SetUnlocked(value)
    unlocked = value
    anchor:EnableMouse(value)
    if value then
        overlay:Show()
        label:Show()
        Print("unlocked. Drag the blue box, then type /rollmove again to lock.")
    else
        StopDrag()
        overlay:Hide()
        label:Hide()
        Print("locked. Tip: Shift + drag moves a roll window while it is up.")
    end
end

local function Setup()
    local target = GetTarget()
    if not target then
        Print("could not find the roll window in this game version.")
        return
    end

    -- Size the drag box like the first roll window and the space it gets in the stack.
    local sample = GroupLootFrame1
    if sample and sample:GetWidth() > 0 then
        baseWidth = sample:GetWidth()
        baseHeight = sample:GetHeight()
    end
    if GroupLootContainer and type(GroupLootContainer.reservedSize) == "number" then
        baseHeight = GroupLootContainer.reservedSize
    end

    PlaceAnchor()

    -- Whenever the default UI places the roll window, pin it to our anchor again.
    hooksecurefunc(target, "SetPoint", function()
        if not applying then AttachTarget() end
    end)
    AttachTarget()
    ApplyScale()

    -- Shift + drag on the roll windows themselves.
    ForEachRollFrame(function(frame)
        frame:EnableMouse(true)
        frame:HookScript("OnMouseDown", StartDrag)
        frame:HookScript("OnMouseUp", StopDrag)
    end)
end

anchor:RegisterEvent("ADDON_LOADED")
anchor:RegisterEvent("PLAYER_LOGIN")
anchor:SetScript("OnEvent", function(self, event, name)
    if event == "ADDON_LOADED" and name == ADDON_NAME then
        CamelusMovableRollFrameDB = CamelusMovableRollFrameDB or {}
        db = CamelusMovableRollFrameDB
        for k, v in pairs(DEFAULTS) do
            if db[k] == nil then db[k] = v end
        end
        self:UnregisterEvent("ADDON_LOADED")
    elseif event == "PLAYER_LOGIN" then
        Setup()
    end
end)

SLASH_CAMELUSMOVABLEROLLFRAME1 = "/rollmove"
SLASH_CAMELUSMOVABLEROLLFRAME2 = "/mrf"
SlashCmdList["CAMELUSMOVABLEROLLFRAME"] = function(msg)
    msg = string.lower(msg or "")
    local cmd, arg = string.match(msg, "^%s*(%S*)%s*(.-)%s*$")

    if cmd == "" then
        SetUnlocked(not unlocked)
    elseif cmd == "unlock" then
        SetUnlocked(true)
    elseif cmd == "lock" then
        SetUnlocked(false)
    elseif cmd == "reset" then
        for k, v in pairs(DEFAULTS) do db[k] = v end
        PlaceAnchor()
        AttachTarget()
        ApplyScale()
        Print("position and size reset.")
    elseif cmd == "scale" then
        local value = tonumber(arg)
        if value and value >= 0.5 and value <= 2 then
            db.scale = value
            PlaceAnchor()
            AttachTarget()
            ApplyScale()
            Print("scale set to " .. value .. ".")
        else
            Print("use a number between 0.5 and 2, e.g. /rollmove scale 1.2")
        end
    else
        Print("commands: /rollmove (lock/unlock), /rollmove reset, /rollmove scale <0.5-2>. Shift + drag moves a roll window.")
    end
end
