from django.test import TestCase
from core.models import Game, GameStatus, GameMode
from django.utils import timezone


class GameModelTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(rows=9, columns=9, mines=10, mode=GameMode.EASY)

    def test_game_is_active_by_default(self):
        self.assertTrue(self.game.is_active())

    def test_game_duration_is_none_on_active_game(self):
        self.assertTrue(self.game.is_active())
        self.assertIsNone(self.game.finished_at)
        self.assertIsNone(self.game.duration)

    def test_game_duration_is_not_none_on_finished_game(self):
        self.game.status = GameStatus.WON
        self.game.finished_at = timezone.now()
        self.game.save()
        self.assertIsNotNone(self.game.duration)
