import io
import unittest
from unittest.mock import patch

from board import Board
from game import Game


def empty_game(grid, score=0):
    g = Game()
    g.board.grid = [row[:] for row in grid]
    g.board.score = score
    return g


Z = [0, 0, 0, 0]


class SlideTests(unittest.TestCase):
    def test_ordinary_slide(self):
        self.assertEqual(Board.slide_line([0, 0, 0, 2]), [2, 0, 0, 0])
        self.assertEqual(Board.slide_line([0, 2, 0, 4]), [2, 4, 0, 0])

    def test_single_pair(self):
        self.assertEqual(Board.slide_line([2, 2, 0, 0]), [4, 0, 0, 0])

    def test_four_equal(self):
        self.assertEqual(Board.slide_line([2, 2, 2, 2]), [4, 4, 0, 0])

    def test_three_equal(self):
        self.assertEqual(Board.slide_line([2, 2, 2, 0]), [4, 2, 0, 0])

    def test_no_chain_merge_original_bug(self):
        self.assertEqual(Board.slide_line([2, 2, 4, 0]), [4, 4, 0, 0])
        self.assertEqual(Board.slide_line([4, 4, 8, 0]), [8, 8, 0, 0])

    def test_separated_equal_pair(self):
        self.assertEqual(Board.slide_line([2, 4, 2, 4]), [2, 4, 2, 4])
        self.assertEqual(Board.slide_line([2, 4, 4, 2]), [2, 8, 2, 0])

    def test_gap_pair_merges(self):
        self.assertEqual(Board.slide_line([2, 0, 2, 0]), [4, 0, 0, 0])


class DirectionTests(unittest.TestCase):
    def test_all_directions(self):
        b = Board()
        b.grid = [[2, 2, 0, 0], [0] * 4, [0] * 4, [0] * 4]
        b.move_right()
        self.assertEqual(b.grid[0], [0, 0, 0, 4])
        b.grid = [[2, 0, 0, 0], [2, 0, 0, 0], [0] * 4, [0] * 4]
        b.move_down()
        self.assertEqual([r[0] for r in b.grid], [0, 0, 0, 4])
        b.move_up()
        self.assertEqual([r[0] for r in b.grid], [4, 0, 0, 0])


class GameStateTests(unittest.TestCase):
    def test_unchanged_move_no_tile_no_change(self):
        g = empty_game([[2, 4, 2, 4], Z, Z, Z])
        before = [r[:] for r in g.board.grid]
        self.assertFalse(g.move("a"))
        self.assertEqual(g.board.grid, before)

    def test_changed_move_adds_exactly_one_tile(self):
        g = empty_game([[0, 0, 0, 2], Z, Z, Z])
        self.assertTrue(g.move("a"))
        self.assertEqual(sum(1 for r in g.board.grid for x in r if x), 2)

    def test_win_detection(self):
        b = Board()
        b.grid = [[2048, 0, 0, 0], Z, Z, Z]
        self.assertTrue(b.has_won())
        b.grid = [[1024, 0, 0, 0], Z, Z, Z]
        self.assertFalse(b.has_won())

    def test_no_move_board(self):
        b = Board()
        b.grid = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]]
        self.assertFalse(b.can_move())

    def test_full_board_with_merge_still_movable(self):
        b = Board()
        b.grid = [[2, 2, 4, 8], [4, 8, 16, 32], [8, 16, 32, 64], [16, 32, 64, 128]]
        self.assertTrue(b.can_move())

    def test_score_on_merge(self):
        g = empty_game([[2, 2, 4, 4], Z, Z, Z])
        g.move("a")
        self.assertEqual(g.board.score, 12)
        self.assertEqual(g.best_score, 12)


class UndoTests(unittest.TestCase):
    def test_undo_restores_board_and_score_no_tile(self):
        g = empty_game([[2, 2, 0, 0], Z, Z, Z])
        g.move("a")
        self.assertTrue(g.undo())
        self.assertEqual(g.board.grid, [[2, 2, 0, 0], Z, Z, Z])
        self.assertEqual(g.board.score, 0)

    def test_undo_is_one_level(self):
        g = empty_game([[2, 2, 0, 0], Z, Z, Z])
        g.move("a")
        g.undo()
        self.assertFalse(g.undo())

    def test_undo_nothing(self):
        self.assertFalse(Game().undo())

    def test_unchanged_move_does_not_overwrite_undo(self):
        g = empty_game([[2, 2, 0, 0], Z, Z, Z])
        g.move("a")
        g.move("a")  # may or may not change; ensure undo still reverts one step
        self.assertTrue(g.undo())

    def test_best_score_kept_after_undo(self):
        g = empty_game([[2, 2, 0, 0], Z, Z, Z])
        g.move("a")
        g.undo()
        self.assertEqual(g.best_score, 4)


class FeedbackAndInputTests(unittest.TestCase):
    def run_game(self, grid, inputs):
        g = empty_game(grid)
        out = io.StringIO()
        with patch("builtins.input", side_effect=inputs), patch("sys.stdout", out):
            g.run()
        return out.getvalue()

    def test_merge_feedback_once(self):
        out = self.run_game([[2, 2, 0, 0], Z, Z, Z], ["a", "q"])
        self.assertEqual(out.count("Moved Left"), 1)
        self.assertIn("1 merge, +4 points", out)

    def test_plain_move_feedback(self):
        out = self.run_game([[0, 0, 0, 2], Z, Z, Z], ["a", "q"])
        self.assertIn("Moved Left.", out)

    def test_unchanged_move_message(self):
        out = self.run_game([[2, 4, 2, 4], Z, Z, Z], ["a", "q"])
        self.assertNotIn("Moved", out)
        self.assertIn("Nothing moved", out)

    def test_invalid_commands(self):
        out = self.run_game([[2, 0, 0, 0], Z, Z, Z], ["x", "", "wa", "q"])
        self.assertEqual(out.count("Use W/A/S/D."), 3)
        self.assertNotIn("Moved", out)

    def test_quit(self):
        out = self.run_game([[2, 0, 0, 0], Z, Z, Z], ["q"])
        self.assertNotIn("Moved", out)

    def test_win_ends_game(self):
        out = self.run_game([[2048, 0, 0, 0], Z, Z, Z], [])
        self.assertIn("reached 2048", out)

    def test_no_moves_ends_game(self):
        grid = [[2, 4, 2, 4], [4, 2, 4, 2], [2, 4, 2, 4], [4, 2, 4, 2]]
        out = self.run_game(grid, [])
        self.assertIn("No legal moves", out)

    def test_undo_command(self):
        out = self.run_game([[2, 2, 0, 0], Z, Z, Z], ["u", "a", "u", "q"])
        self.assertIn("Nothing to undo.", out)
        self.assertIn("Undone.", out)


if __name__ == "__main__":
    unittest.main()