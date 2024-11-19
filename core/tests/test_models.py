from django.test import TestCase
from core.models import Game, GameStatus, GameMode, Cell
from django.utils import timezone


class GameModelTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(rows=9, columns=9, mines=10, mode=GameMode.EASY)

    def test_game_is_active_by_default(self):
        self.assertTrue(self.game.is_active())

    def test_game_str_method(self):
        self.assertEqual(str(self.game), f"Game {self.game.id}")

    def test_game_duration_is_none_on_active_game(self):
        self.assertTrue(self.game.is_active())
        self.assertIsNone(self.game.finished_at)
        self.assertIsNone(self.game.duration)

    def test_game_duration_is_not_none_on_finished_game(self):
        self.game.status = GameStatus.WON
        self.game.finished_at = timezone.now()
        self.game.save()
        self.assertIsNotNone(self.game.duration)


class CellModelTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            rows=9, columns=9, mines=10, mode=GameMode.EASY
        )
        self.cell = Cell.objects.create(
            game=self.game, row=1, column=1, is_mine=True
        )

    def test_cell_str_method(self):
        self.assertEqual(str(self.cell), f"Cell {self.cell.row}x{self.cell.column} - Game {self.cell.game.id}")
