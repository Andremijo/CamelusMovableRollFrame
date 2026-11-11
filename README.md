# Camelus' Movable Roll Frame

A small World of Warcraft addon that makes the Need / Greed / Pass roll window movable.
Written for the 3.3.5 (WotLK) client. It also has a TOC file for WotLK Classic.

## Install

1. Go to [Releases](../../releases/latest) and download **CamelusMovableRollFrame-Forever.zip**.
2. Unzip it into `World of Warcraft\Interface\AddOns\`, so you get
   `Interface\AddOns\CamelusMovableRollFrame\CamelusMovableRollFrame.toc`.
3. Restart the game and make sure "Camelus' Movable Roll Frame" is ticked in the AddOns list.

(If you use Code → Download ZIP instead, rename the folder from `CamelusMovableRollFrame-main` to `CamelusMovableRollFrame`. WoW only loads the addon if the folder name matches the `.toc` file.)

## Making a new release

1. Update `## Version:` in both `.toc` files.
2. On GitHub, go to Releases → "Draft a new release", create a new tag such as `v1.1`, and publish.
3. A minute later, GitHub has built `CamelusMovableRollFrame-Forever.zip` and attached it to the release.

## Use

| Command / action | What it does |
| --- | --- |
| `/rollmove` (or `/mrf`) | Shows a blue box where the roll window appears. Drag it, then type `/rollmove` again to lock. |
| Shift + left-drag on a roll window | Moves it while a roll is up. |
| `/rollmove scale 1.2` | Makes the roll windows bigger or smaller (0.5 – 2). |
| `/rollmove reset` | Back to the default spot and size. |

The position is saved per character.

When several items drop at once, the extra roll windows stack on top of the first one as usual.
