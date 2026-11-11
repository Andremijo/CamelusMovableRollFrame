<img src="media/icon.png" width="96" align="right" alt="Camelus' Movable Roll Frame icon">

# Camelus' Movable Roll Frame

A small addon for **WoW Forever** that makes the Need / Greed / Pass roll window movable.

## Install

1. Go to [Releases](../../releases/latest) and download **CamelusMovableRollFrame-Forever.zip**.
2. Unzip it into your game's `Interface\AddOns\` folder, so you get
   `Interface\AddOns\CamelusMovableRollFrame\CamelusMovableRollFrame.toc`.
3. Restart the game and make sure "Camelus' Movable Roll Frame" is ticked in the AddOns list.

(If you use Code → Download ZIP instead, rename the folder from `CamelusMovableRollFrame-main` to `CamelusMovableRollFrame`. WoW only loads the addon if the folder name matches the `.toc` file.)

## Use

| Command / action | What it does |
| --- | --- |
| `/rollmove` (or `/mrf`) | Shows a blue box where the roll window appears. Drag it, then type `/rollmove` again to lock. |
| Shift + left-drag on a roll window | Moves it while a roll is up. |
| `/rollmove scale 1.2` | Makes the roll windows bigger or smaller (0.5 – 2). |
| `/rollmove reset` | Back to the default spot and size. |

The position is saved per character.

When several items drop at once, the extra roll windows stack on top of the first one as usual.
Loot toasts ("You received ...") that appear while a roll is up stack above the roll windows, wherever you put them.

## Making a new release

1. Change `## Version:` in `CamelusMovableRollFrame.toc`, for example to `1.2`, and push to `main`.
2. A minute later, GitHub has created release `v1.2` with `CamelusMovableRollFrame-Forever.zip` and `release.json` attached.

Pushes that don't change the version don't create a release.
