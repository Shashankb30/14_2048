import random

SIZE = 4
WIN_TILE = 2048


class Board:
    def __init__(self):
        self.grid = [[0] * SIZE for _ in range(SIZE)]
        self.score = 0
        self.last_gain = 0      # points scored by the most recent move
        self.last_merges = 0    # merges made by the most recent move
        self.add_random_tile()
        self.add_random_tile()

    def add_random_tile(self):
        empty = [(r, c) for r in range(SIZE) for c in range(SIZE) if self.grid[r][c] == 0]
        if empty:
            r, c = random.choice(empty)
            self.grid[r][c] = 4 if random.random() < 0.1 else 2

    @staticmethod
    def slide_line_scored(line):
        """Slide a line toward index 0.

        Returns (new_line, points_gained, merge_count). Every original tile
        takes part in at most one merge: after two tiles merge we skip both
        (i += 2), so the new tile can never merge again in the same move.
        """
        values = [x for x in line if x]
        result, gained, merges = [], 0, 0
        i = 0
        while i < len(values):
            if i + 1 < len(values) and values[i] == values[i + 1]:
                merged = values[i] * 2
                result.append(merged)
                gained += merged
                merges += 1
                i += 2
            else:
                result.append(values[i])
                i += 1
        return result + [0] * (SIZE - len(result)), gained, merges

    @staticmethod
    def slide_line(line):
        return Board.slide_line_scored(line)[0]

    def _get_line(self, i, direction):
        """Line i, oriented so that sliding toward index 0 means 'move in direction'."""
        if direction == "left":
            return self.grid[i][:]
        if direction == "right":
            return self.grid[i][::-1]
        col = [self.grid[r][i] for r in range(SIZE)]
        return col if direction == "up" else col[::-1]

    def _set_line(self, i, direction, line):
        if direction == "left":
            self.grid[i] = line
        elif direction == "right":
            self.grid[i] = line[::-1]
        else:
            col = line if direction == "up" else line[::-1]
            for r in range(SIZE):
                self.grid[r][i] = col[r]

    def _move(self, direction):
        changed, gain, merges = False, 0, 0
        for i in range(SIZE):
            old = self._get_line(i, direction)
            new, g, m = self.slide_line_scored(old)
            if new != old:
                changed = True
                self._set_line(i, direction, new)
            gain += g
            merges += m
        self.score += gain
        self.last_gain = gain if changed else 0
        self.last_merges = merges if changed else 0
        return changed

    def move_left(self):
        return self._move("left")

    def move_right(self):
        return self._move("right")

    def move_up(self):
        return self._move("up")

    def move_down(self):
        return self._move("down")

    def has_won(self):
        return any(WIN_TILE in row for row in self.grid)

    def can_move(self):
        if any(0 in row for row in self.grid):
            return True
        for r in range(SIZE):
            for c in range(SIZE):
                if c + 1 < SIZE and self.grid[r][c] == self.grid[r][c + 1]:
                    return True
                if r + 1 < SIZE and self.grid[r][c] == self.grid[r + 1][c]:
                    return True
        return False

    def snapshot(self):
        """Copy of everything needed to restore this board (grid + score)."""
        return [row[:] for row in self.grid], self.score

    def restore(self, snap):
        self.grid = [row[:] for row in snap[0]]
        self.score = snap[1]