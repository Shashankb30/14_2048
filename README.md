# Scenario 14 — 2048

A terminal 2048 implementation with directional movement and tile merging.

## Provided files

- `main.py` — entry point.
- `game.py` — game loop, commands, and game state.
- `board.py` — grid movement and tile logic.
- `requirements.txt` — dependency declaration.

## Setup

```bash
python main.py
```

No package installation is required.

## Before changing the code

Run the starter and deliberately construct repeated-tile rows if possible. Read the
board movement code and trace one complete move from input to tile creation.

## Task 1 — Correct merge semantics

Fix the merge algorithm so an original tile can participate in at most one merge
during a single move. Preserve normal compression and movement behaviour.

**Done when:** repeated patterns such as four equal tiles produce the standard 2048
result, not a chain merge of a newly created tile in the same move.

## Task 2 — Finish game-state handling

Implement win detection, no-move detection, and correct tile creation semantics.
A move that leaves the board unchanged must not create a new tile.

**Done when:** reaching 2048 ends the game, a full board with no legal moves ends the
game, and unchanged moves do not alter the board.

## Task 3 — Undo and best score

Add a one-level undo. Restoring a move must restore both board contents and score.
Track the best score for the current run.

**Done when:** one undo reverses exactly one successful move and does not create a tile.

## Task 4 — Move feedback

Add concise feedback for successful moves and merges. Do not trigger feedback merely
because internal board-scanning functions were called.

**Done when:** one accepted move produces one action-level result and invalid/unchanged
moves do not claim that a move occurred.

## Required testing

Test ordinary slides, four-equal patterns, separated equal pairs, unchanged moves,
2048 detection, no-move boards, undo, score restoration, invalid commands, and quitting.


## LLM usage

You may use an LLM during the lab. The goal is to use it as a coding assistant while
retaining responsibility for understanding and testing the result.

- Inspect the existing code before asking for changes.
- Ask for explanations when you do not understand a proposed change.
- Test generated code against the stated behaviour and edge cases.
- Keep your complete LLM chat history for submission.
- Do not replace the whole project with an unrelated implementation.
- Keep all state in memory; do not add CSV, JSON, SQLite, or other persistence.

## Submission checklist

- [ ] Task 1 completed and the original defect was reproduced and fixed.
- [ ] Tasks 2–4 completed and tested.
- [ ] Boundary and invalid-input cases tested.
- [ ] No unnecessary external dependencies added.
- [ ] No persistent storage added.
- [ ] Code remains understandable and modular.
- [ ] Complete LLM chat-history link included.

## Folder structure

```text
scenario-02-2048/
├── README.md
├── requirements.txt
├── main.py
├── game.py
└── board.py
```

## Submission Checklist

Submission is only the following three things:

- [ ] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [ ] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [ ] The Chat/LLM used page link, with the complete chat history


---

# My Implementation Notes (Lab 4 — VibeCoding)

This section documents what I changed in the starter code, how each task was
done, and how I tested it. All state is kept in memory. There are no new
dependencies and no file storage.

## Defects found in the starter code

| # | File | Problem |
|---|------|---------|
| 1 | `board.py` | `slide_line` used `result[-1] *= 2`, so a tile created by a merge could merge again in the same move. `[2,2,4,0]` became `[8,0,0,0]` instead of `[4,4,0,0]`. |
| 2 | `board.py` | Merges never added to the score, so the score always stayed at 0. |
| 3 | `game.py` | `key not in "wasd"` is a substring test, so an empty input or `"wa"` slipped through and was silently ignored. |
| 4 | `game.py` | Undo was a stub ("not implemented yet") and there was no move feedback. |

I reproduced the main defect before fixing it: with a row `[2,2,4,0]`, pressing
`a` gave `8` instead of `4 4`. This is shown in the "before" video.

## What I changed, task by task

Each task is a separate commit.

### Task 1 — Correct merge semantics (`board.py`)
- Rewrote `slide_line` as `slide_line_scored`. It walks the compressed tiles by
  index, and after two tiles merge it skips both with `i += 2`. So each original
  tile takes part in at most one merge, and the new tile can never merge again
  in the same move.
- `slide_line` is kept as a thin wrapper that returns just the new line.
- Merging now adds the merged value to `score`, and `last_gain` and
  `last_merges` record what the latest move did (used later for feedback).
- The four near-identical `move_*` methods now share one `_move(direction)`
  helper, with `_get_line` and `_set_line` handling the left, right, up and down
  orientation.

Results: `[2,2,4,0]` gives `[4,4,0,0]`, `[4,4,8,0]` gives `[8,8,0,0]`,
`[2,2,2,2]` gives `[4,4,0,0]`, and `[2,4,2,4]` is unchanged.

### Task 2 — Game-state handling (`board.py`, `game.py`)
- Added `WIN_TILE = 2048` and `Board.has_won()`. The game loop ends with a win
  message when a 2048 tile exists.
- `can_move()` (existing, correct) now drives the "No legal moves" ending: a
  full board with no equal neighbours ends the game.
- `Game.move()` adds a new tile only when the board changed. An unchanged move
  leaves the board exactly as it was and adds nothing.
- Input validation now uses an exact match against a `DIRECTIONS` dictionary
  instead of the substring test, so `""` and `"wa"` correctly print
  "Use W/A/S/D."

### Task 3 — Undo and best score (`board.py`, `game.py`)
- `Board.snapshot()` returns a copy of the grid and score, and
  `Board.restore()` puts them back.
- `Game.move()` saves a snapshot before each move and keeps it only if the move
  succeeded, so an unchanged move can never overwrite the undo state.
- `Game.undo()` restores the board and the score, creates no new tile, and
  clears the saved state. This makes it exactly one level: a second `u` prints
  "Nothing to undo."
- `best_score` is updated after every successful move. Undo does not lower it,
  because it is the best score of the current run.
- The unused `history` list was replaced by `undo_state`.

### Task 4 — Move feedback (`game.py`)
- Added `Game.feedback(key)`, which builds one action-level message from the
  move's `last_merges` and `last_gain`, for example
  `Moved Left: 1 merge, +4 points.` or `Moved Left.`
- `run()` prints exactly one line per move. An unchanged move prints
  `Nothing moved - try another direction.` and never says "Moved".
- Feedback is based on what the finished move did, not on board-scanning helper
  calls, so scanning functions never trigger messages.

## Commit history

1. `fix(board): each tile merges at most once per move; merges add to score`
2. `feat(game): win/no-move detection, strict input validation, tile only on changed move`
3. `feat(game): one-level undo (board+score) and best score`
4. `feat(game): concise move/merge feedback; no claim on unchanged moves`
5. `test: add unit tests covering README required cases`

## Testing

Run the unit tests (standard library only):

```bash
python -m unittest
```

`test_2048.py` has 27 tests. They cover:

- ordinary slides, single pairs, three equal tiles and four equal tiles
- the original chain-merge bug (`[2,2,4,0]` and `[4,4,8,0]`)
- separated equal pairs (`[2,4,2,4]`)
- all four move directions
- unchanged moves (no change to the board, no new tile)
- 2048 detection and no-move boards
- score on merge and best score
- undo: board and score restored, no tile created, only one level, nothing to undo
- feedback printed once per accepted move, and none for unchanged moves
- invalid commands (`x`, empty input, `wa`) and quitting with `q`

Quick one-line checks:

```bash
python -c "from board import Board; print(Board.slide_line([2,2,4,0]), Board.slide_line([2,2,2,2]))"
# expected: [4, 4, 0, 0] [4, 4, 0, 0]
```

## How to play

```bash
python main.py
```

`W/A/S/D` move, `U` undoes the last move, `Q` quits.

## Submission contents (Lab-4)

- Before video: `before.mp4` (shows the double-merge bug, score stuck at 0, undo not implemented)
- After video: `after.mp4` (shows the fix, score, feedback messages, undo, invalid input, quit)
- Updated code: `main.py`, `game.py`, `board.py`, `test_2048.py`
- LLM chat history: <paste chat link here>