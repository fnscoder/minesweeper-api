from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.constants import (
    CANNOT_FLAG_REVEALED_CELL,
    CELL_ALREADY_REVEALED,
    CELL_NOT_FOUND,
    GAME_NOT_ACTIVE,
    MINES_MUST_BE_SMALLER_THAN_CELLS, ROWS_COLS_MINES_REQUIRED,
)
from core.models import Game, GameStatus, GameMode, Cell
from core.services import GameService


class GameViewSetTest(TestCase):
    """Test module for Game viewset"""

    def setUp(self):
        """set up test creating a game and initialize cells"""
        self.client = APIClient()
        self.game = Game.objects.create(rows=9, columns=9, mines=10, mode=GameMode.EASY)
        GameService.initialize_cells(self.game)
        self.url_list = reverse("game-list")
        self.url_flag = reverse("game-flag", args=[self.game.id])
        self.url_reveal = reverse("game-reveal", args=[self.game.id])

    def test_create_game_easy_mode(self):
        """Test creating a new game with easy mode"""
        data = {"mode": GameMode.EASY}

        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 2)

    def test_create_game_custom_mode(self):
        """Test creating a new game with custom mode"""
        data = {"rows": 5, "columns": 5, "mines": 2, "mode": GameMode.CUSTOM}

        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 2)

    def test_retrieve_game(self):
        """Test retrieving an existing game"""
        url = reverse("game-detail", args=[self.game.id])
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.game.id)

    def test_retrieve_nonexistent_game(self):
        """Test retrieving a nonexistent game"""
        url = reverse("game-detail", args=[999])
        response = self.client.get(url, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_game_custom_mode_invalid_options(self):
        """ " Test creating a new game with custom mode and invalid options"""
        data = {"rows": 5, "columns": 5, "mines": 30, "mode": GameMode.CUSTOM}

        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["mines"][0], MINES_MUST_BE_SMALLER_THAN_CELLS)

    def test_create_game_custom_mode_missing_fields(self):
        """ " Test creating a new game with custom mode missing required fields"""
        data = {"mode": GameMode.CUSTOM}

        response = self.client.post(self.url_list, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["required"][0], ROWS_COLS_MINES_REQUIRED)

    def test_flag_cell_active_game(self):
        """Test flagging a cell in an active game"""
        data = {"row": 1, "column": 1}

        response = self.client.post(self.url_flag, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_flagged"], True)

    def test_flag_cell_inactive_game(self):
        """Test flagging a cell in an inactive game"""
        self.game.status = GameStatus.WON
        self.game.save()
        data = {"row": 1, "column": 1}

        response = self.client.post(self.url_flag, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, GAME_NOT_ACTIVE)

    def test_flag_revealed_cell(self):
        """Test flagging a revealed cell"""
        clean_cell = Cell.objects.filter(game=self.game, is_mine=False).first()
        data = {"row": clean_cell.row, "column": clean_cell.column}
        self.client.post(self.url_reveal, data, format="json")

        response = self.client.post(self.url_flag, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, CANNOT_FLAG_REVEALED_CELL)

    def test_flag_cell_nonexistent_cell(self):
        """Test flagging a nonexistent cell"""
        data = {"row": 99, "column": 99}

        response = self.client.post(self.url_flag, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, CELL_NOT_FOUND)

    def test_unflag_flagged_cell_active_game(self):
        """Test unflagging a flagged cell in an active game"""
        data = {"row": 1, "column": 1}

        response = self.client.post(self.url_flag, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_flagged"], True)

        response = self.client.post(self.url_flag, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["is_flagged"], False)

    def test_reveal_clean_cell(self):
        """Test revealing a clean cell"""
        clean_cell = Cell.objects.filter(game=self.game, is_mine=False).first()
        data = {"row": clean_cell.row, "column": clean_cell.column}

        response = self.client.post(self.url_reveal, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reveal_flagged_cell(self):
        """Test revealing a flagged cell"""
        flagged_cell = Cell.objects.filter(game=self.game, is_mine=False).first()
        flagged_cell.toggle_flag()
        self.assertEqual(flagged_cell.is_flagged, True)
        data = {"row": flagged_cell.row, "column": flagged_cell.column}

        response = self.client.post(self.url_reveal, data, format="json")

        flagged_cell.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(flagged_cell.is_flagged, False)

    def test_reveal_nonexistent_cell(self):
        """Test revealing a nonexistent cell"""
        data = {"row": 99, "column": 99}

        response = self.client.post(self.url_reveal, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, CELL_NOT_FOUND)

    def test_reveal_clean_cell_twice(self):
        """Test revealing a clean cell"""
        clean_cell = Cell.objects.filter(game=self.game, is_mine=False).first()
        data = {"row": clean_cell.row, "column": clean_cell.column}

        self.client.post(self.url_reveal, data, format="json")
        response = self.client.post(self.url_reveal, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, CELL_ALREADY_REVEALED)

    def test_reveal_mine_cell(self):
        """Test revealing a mine cell"""
        mine_cell = Cell.objects.filter(game=self.game, is_mine=True).first()
        data = {"row": mine_cell.row, "column": mine_cell.column}

        response = self.client.post(self.url_reveal, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], GameStatus.LOST)

    def test_reveal_cell_inactive_game(self):
        """Test revealing a cell in an inactive game"""
        self.game.status = GameStatus.WON
        self.game.save()
        data = {"row": 1, "column": 1}

        response = self.client.post(self.url_reveal, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, GAME_NOT_ACTIVE)

    def test_win_game(self):
        """Test winning a game"""
        excluded_cell = Cell.objects.filter(game=self.game, is_mine=False).first()
        clean_cells = Cell.objects.filter(game=self.game, is_mine=False).exclude(
            id=excluded_cell.id
        )
        for cell in clean_cells:
            cell.is_revealed = True
            cell.save()
        data = {"row": excluded_cell.row, "column": excluded_cell.column}

        response = self.client.post(self.url_reveal, data, format="json")

        self.game.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.game.status, GameStatus.WON)
