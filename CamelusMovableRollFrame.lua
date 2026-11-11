-- Camelus' Movable Roll Frame
-- Makes the Need / Greed / Pass roll window movable.
--
--   Shift + left-drag on a roll window   -> move it while a roll is up
--   /rollmove                            -> show/hide a drag handle (works with no roll up)
--   /rollmove reset                      -> back to the default spot
--   /rollmove scale 1.2                  -> make the roll windows bigger/smaller (0.5 - 2)

local ADDON_NAME = "CamelusMovableRollFrame"
local DEFAULTS = { point = "BOTTOM", relPoint = "BOTTOM", x = 0, y = 200, scale = 1 }

local db
local unlocked = false
local applying = false

local function Print(msg)
    DEFAULT_CHAT_FRAME:AddMessage("|cff33ccffCamelus' Movable Roll Frame|r: " .. msg)
end

-- Our own invisible anchor. The roll window is pinned to it, and we move the anchor.
local anchor = CreateFrame("Frame", "CamelusMovableRollFrameAnchor", UIParent)
anchor:SetWidth(280)
anchor:SetHeight(70)
anchor:SetFrameStrata("DIALOG")
anchor:SetMovable(true)
anchor:SetClampedToScreen(true)
anchor:EnableMouse(false)

local overlay = anchor:CreateTexture(nil, "OVERLAY")
overlay:SetAllPoints(anchor)
if overlay.SetColorTexture then
    overlay:SetColorTexture(0, 0.6, 1, 0.4)
else
    overlay:SetTexture(0, 0.6, 1, 0.4)
end
overlay:Hide()

local label = anchor:CreateFontString(nil, "OVERLAY", "GameFontNormal")
label:SetPoint("CENTER", anchor, "CENTER", 0, 0)
label:SetText("Roll window\nDrag me, then type /rollmove to lock")
label:Hide()

-- Newer clients put all roll windows in GroupLootContainer; 3.3.5 stacks
-- GroupLootFrame2-4 on top of GroupLootFrame1. Either way we move the bottom one.
local function GetTarget()
    return GroupLootContainer or GroupLootFrame1
end

local function PlaceAnchor()
    anchor:ClearAllPoints()
    anchor:SetPoint(db.point, UIParent, db.relPoint, db.x, db.y)
    anchor:SetScale(db.scale)
end

local function AttachTarget()
    local target = GetTarget()
    if not target or applying then return end
    applying = true
    target:ClearAllPoints()
    target:SetPoint("BOTTOM", anchor, "BOTTOM", 0, 0)
    target:SetScale(db.scale)
    applying = false
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
    local sample = GroupLootFrame1
    if sample and sample:GetWidth() > 0 then
        anchor:SetWidth(sample:GetWidth())
        anchor:SetHeight(sample:GetHeight())
    end

    PlaceAnchor()

    local target = GetTarget()
    if not target then
        Print("could not find the roll window in this game version.")
        return
    end

    -- Whenever the default UI tries to put the roll window back, pin it to our anchor again.
    hooksecurefunc(target, "SetPoint", function()
        if not applying then AttachTarget() end
    end)
    AttachTarget()

    -- Shift + drag on the roll windows themselves.
    for i = 1, (NUM_GROUP_LOOT_FRAMES or 4) do
        local frame = _G["GroupLootFrame" .. i]
        if frame then
            frame:EnableMouse(true)
            frame:HookScript("OnMouseDown", StartDrag)
            frame:HookScript("OnMouseUp", StopDrag)
        end
    end
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
    elseif event == "PLAYER_LOGIN" then
        Setup()
    end
end)

SLASH_CAMELUSMOVABLEROLLFRAME1 = "/rollmove"
SLASH_CAMELUSMOVABLEROLLFRAME2 = "/mrf"
SlashCmdList["CAMELUSMOVABLEROLLFRAME"] = function(msg)
    msg = string.lower(msg or "")
    local cmd, arg = string.match(msg, "^%s*(%S*)%s*(.-)%s*$")

    if cmd == "" or cmd == "lock" or cmd == "unlock" then
        if cmd == "lock" then
            SetUnlocked(false)
        elseif cmd == "unlock" then
            SetUnlocked(true)
        else
            SetUnlocked(not unlocked)
        end
    elseif cmd == "reset" then
        for k, v in pairs(DEFAULTS) do db[k] = v end
        PlaceAnchor()
        AttachTarget()
        Print("position and size reset.")
    elseif cmd == "scale" then
        local value = tonumber(arg)
        if value and value >= 0.5 and value <= 2 then
            db.scale = value
            PlaceAnchor()
            AttachTarget()
            Print("scale set to " .. value .. ".")
        else
            Print("use a number between 0.5 and 2, e.g. /rollmove scale 1.2")
        end
    else
        Print("commands: /rollmove (lock/unlock), /rollmove reset, /rollmove scale <0.5-2>. Shift + drag moves a roll window.")
    end
end
