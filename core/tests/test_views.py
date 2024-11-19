from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Game, GameStatus, GameMode, Cell
from core.services import GameService


class GameViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.game = Game.objects.create(rows=9, columns=9, mines=10, mode=GameMode.EASY)
        GameService.initialize_cells(self.game)

    def test_create_game_easy_mode(self):
        url = reverse("game-list")
        data = {"mode": GameMode.EASY}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 2)

    def test_create_game_custom_mode(self):
        url = reverse("game-list")
        data = {"rows": 5, "columns": 5, "mines": 2, "mode": GameMode.CUSTOM}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 2)

    def test_create_game_custom_mode_invalid_options(self):
        url = reverse("game-list")
        data = {"rows": 5, "columns": 5, "mines": 30, "mode": GameMode.CUSTOM}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data, {"mines": ["mines should be smaller than rows * columns"]}
        )

    def test_flag_cell_active_game(self):
        url = reverse("game-flag", args=[self.game.id])
        data = {"row": 1, "column": 1}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_flag_cell_inactive_game(self):
        self.game.status = GameStatus.WON
        self.game.save()
        url = reverse("game-flag", args=[self.game.id])
        data = {"row": 1, "column": 1}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Game is not active"})

    def test_reveal_clean_cell(self):
        mine_cell = Cell.objects.filter(game=self.game, is_mine=False).first()
        url = reverse("game-reveal", args=[self.game.id])
        data = {"row": mine_cell.row, "column": mine_cell.column}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reveal_clean_cell_twice(self):
        mine_cell = Cell.objects.filter(game=self.game, is_mine=False).first()
        url = reverse("game-reveal", args=[self.game.id])
        data = {"row": mine_cell.row, "column": mine_cell.column}
        self.client.post(url, data, format="json")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Cell already revealed"})

    def test_reveal_mine_cell(self):
        mine_cell = Cell.objects.filter(game=self.game, is_mine=True).first()
        url = reverse("game-reveal", args=[self.game.id])
        data = {"row": mine_cell.row, "column": mine_cell.column}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], GameStatus.LOST)

    def test_reveal_cell_inactive_game(self):
        self.game.status = GameStatus.WON
        self.game.save()
        url = reverse("game-reveal", args=[self.game.id])
        data = {"row": 1, "column": 1}
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "Game is not active"})
