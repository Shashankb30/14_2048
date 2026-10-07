from board import Board

DIRECTIONS = {"a": "left", "d": "right", "w": "up", "s": "down"}


class Game:
    def __init__(self):
        self.board = Board()
        self.best_score = 0
        self.undo_state = None   # one level only: state before the last successful move

    def display(self):
        print("\n" + "+------+------+------+------+")
        for row in self.board.grid:
            print("|" + "|".join(f"{x:^6}" if x else f"{' ':^6}" for x in row) + "|")
            print("+------+------+------+------+")
        print("Score:", self.board.score, " Best:", self.best_score)

    def move(self, key):
        """Apply a move. Returns True only if the board changed.

        A new tile is added only after a successful (changing) move.
        """
        if key not in DIRECTIONS:
            return False
        before = self.board.snapshot()
        changed = getattr(self.board, f"move_{DIRECTIONS[key]}")()
        if changed:
            self.undo_state = before
            self.board.add_random_tile()
            self.best_score = max(self.best_score, self.board.score)
        return changed

    def undo(self):
        """Revert the last successful move (board + score). No tile is created.

        Best score is kept: it is the best of the current run. Returns False
        if there is nothing to undo.
        """
        if self.undo_state is None:
            return False
        self.board.restore(self.undo_state)
        self.undo_state = None
        return True

    def run(self):
        print("2048 — W/A/S/D to move, U to undo, Q to quit.")
        while True:
            self.display()
            if self.board.has_won():
                print("You reached 2048! You win!")
                return
            if not self.board.can_move():
                print("No legal moves remain. Game over.")
                return
            key = input("> ").strip().lower()
            if key == "q":
                return
            if key == "u":
                print("Undone." if self.undo() else "Nothing to undo.")
                continue
            if key not in DIRECTIONS:   # exact match (the old substring test let "" and "wa" through)
                print("Use W/A/S/D.")
                continue
            self.move(key)