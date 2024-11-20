from django.test import TestCase
from core.models import Game, GameStatus, GameMode, Cell
from django.utils import timezone


class GameModelTest(TestCase):
    """Test module for Game model"""

    def setUp(self):
        """set up test creating a game"""
        self.game = Game.objects.create(rows=9, columns=9, mines=10, mode=GameMode.EASY)

    def test_game_is_active_by_default(self):
        """Test if the game is active by default"""
        self.assertTrue(self.game.is_active())

    def test_game_str_method(self):
        """Test the string representation of the game"""
        self.assertEqual(str(self.game), f"Game {self.game.id}")

    def test_game_duration_is_none_on_active_game(self):
        """Test if the duration is None on an active game"""
        self.assertTrue(self.game.is_active())
        self.assertIsNone(self.game.finished_at)
        self.assertIsNone(self.game.duration)

    def test_game_duration_is_not_none_on_finished_game(self):
        """Test if the duration is not None on a finished game"""
        self.game.end_game(GameStatus.WON)

        self.assertFalse(self.game.is_active())
        self.assertIsNotNone(self.game.duration)


class CellModelTest(TestCase):
    """Test module for Game model"""

    def test_cell_str_method(self):
        """Test the string representation of the cell"""
        game = Game.objects.create(rows=9, columns=9, mines=10, mode=GameMode.EASY)
        cell = Cell.objects.create(game=game, row=1, column=1, is_mine=True)

        self.assertEqual(
            str(cell),
            f"Cell {cell.row}x{cell.column} - Game {cell.game.id}",
        )
