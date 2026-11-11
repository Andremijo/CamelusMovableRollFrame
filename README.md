# Camelus' Movable Roll Frame

A small World of Warcraft addon that makes the Need / Greed / Pass roll window movable.
Written for the 3.3.5 (WotLK) client. It also has a TOC file for WotLK Classic.

## Install

1. Download the repository (Code → Download ZIP) and unzip it.
2. Rename the folder to exactly `CamelusMovableRollFrame`. GitHub calls it `CamelusMovableRollFrame-main`, and WoW only loads the addon if the folder name matches the `.toc` file.
3. Put the folder in `World of Warcraft\Interface\AddOns\`, so you get
   `Interface\AddOns\CamelusMovableRollFrame\CamelusMovableRollFrame.toc`.
4. Restart the game and make sure "Camelus' Movable Roll Frame" is ticked in the AddOns list.

## Use

| Command / action | What it does |
| --- | --- |
| `/rollmove` (or `/mrf`) | Shows a blue box where the roll window appears. Drag it, then type `/rollmove` again to lock. |
| Shift + left-drag on a roll window | Moves it while a roll is up. |
| `/rollmove scale 1.2` | Makes the roll windows bigger or smaller (0.5 – 2). |
| `/rollmove reset` | Back to the default spot and size. |

The position is saved per character.

When several items drop at once, the extra roll windows stack on top of the first one as usual.
