# Camelus' Movable Roll Frame: notes for Claude

World of Warcraft addon for **WoW Forever** that makes the Need/Greed roll window movable. Sister addon: Camelus' Enhanced Quest Log (repo `Andremijo/CamelusEnhancedQuestLog`), whose CLAUDE.md has more background on the client.

## Working on this project
- The owner is not a programmer. Explain changes in plain language and say what they mean in practice.
- Reply in the language of the latest message (English or Swedish).
- You cannot run WoW. Say plainly what has and hasn't been tested in the game.

## The client
- WoW Forever, **Interface 16001**. Its UI is the retail ("Mainline") UI with overrides. The `.toc` must say 16001, or the game lists the addon as "Incompatible".
- Blizzard's UI source for this client: **Gethe/wow-ui-source, branch `forever`**. Read it instead of guessing. Sparse, blob-less clone:
  ```bash
  GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 --branch forever --filter=blob:none --sparse https://github.com/Gethe/wow-ui-source ~/wow-ui-source
  git -C ~/wow-ui-source sparse-checkout set --no-cone '/Interface/AddOns/Blizzard_UIPanels_Game/Mainline/GroupLootFrame*' '/Interface/AddOns/Blizzard_ManagedFrameSystem/'
  ```
- The roll window: `Blizzard_UIPanels_Game/Mainline/GroupLootFrame.lua/.xml`. `GroupLootFrame1-4` (277×67) are children of UIParent. `GroupLootContainer` stacks them, each centred at container BOTTOM + `reservedSize` (100) × (i − 0.5). The container is a `BottomManagedFrameTemplate`: `BottomManagedFrameContainer` re-anchors it whenever it is shown or laid out. It is also an externally anchored alert subsystem, so loot toasts stack on it while it is shown.
- Edit Mode in WoW Forever can move the loot window, but not the roll window.

## How the addon works
- An own anchor frame (`CamelusMovableRollFrameAnchor`) is what the player moves. A `hooksecurefunc(GroupLootContainer, "SetPoint", ...)` pins the container back to the anchor every time Blizzard places it.
- Scale is applied to each `GroupLootFrameN` (they are not children of the container) and to the container. The anchor is resized, not scaled, so its saved position doesn't shift.
- **Taint:** never write fields on Blizzard frames and never replace Blizzard functions. Only `hooksecurefunc`, `HookScript` and method calls.
- **Never let a hidden-looking frame catch clicks.** In 1.1 the anchor had mouse scripts. The likely cause of the owner's report (the trade window's Trade button stopped working): setting a mouse script turns mouse input on in the modern client, so the invisible anchor (strata DIALOG) swallowed clicks on whatever was under it. Not confirmed in the game yet. Since 1.2 the anchor has no mouse scripts. The blue drag box is a separate child frame (`mover`) that is hidden while locked. `tests/test_addon.py` checks this (`AddonCatchesClicks`).

## Files
- `CamelusMovableRollFrame.toc`: `## Version:` is the single source of the version number.
- `CamelusMovableRollFrame.lua`: all the code.
- `CamelusMovableRollFrame.tga`: the addon icon (64×64, uncompressed 32-bit TGA). Regenerate with `python3 media/make_icon.py <out_dir>` (Pillow). `media/icon.png` is its `preview_256.png`, used in the README.
- `tests/test_addon.py`: runs the addon in Lua 5.1 (`pip install lupa`) with stand-in frames. Run it after every change: `python3 tests/test_addon.py`.
- `.github/workflows/release.yml`: on every push to `main`, creates release `v<Version>` if it doesn't exist yet, with `CamelusMovableRollFrame-Forever.zip` (the owner wants this exact name) and `release.json` (flavor `forever`, for WoWUp).

## Releasing
Bump `## Version:` in the `.toc` and push to `main`. The workflow does the rest. Pushing tags from a Claude session is refused by the git proxy, so don't try. The workflow can also be started with `workflow_dispatch`.
