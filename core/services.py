from random import sample

from django.db import transaction
from django.utils.timezone import now
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_200_OK

from .constants import CANNOT_FLAG_REVEALED_CELL, CELL_ALREADY_REVEALED, CELL_NOT_FOUND
from .models import Cell, GameStatus
from .serializers import GameSerializer, CellSerializer


class GameService:
    @staticmethod
    def initialize_cells(game):
        cells = GameService._create_cells(game)
        GameService._place_mines(game, cells)
        GameService._calculate_adjacencies(cells)

    @staticmethod
    def _create_cells(game):
        cells = [
            Cell(game=game, row=row, column=col)
            for row in range(game.rows)
            for col in range(game.columns)
        ]
        Cell.objects.bulk_create(cells)
        return Cell.objects.filter(game=game)

    @staticmethod
    def _place_mines(game, cells):
        mine_cells = sample(list(cells), game.mines)
        for mine in mine_cells:
            mine.is_mine = True
        Cell.objects.bulk_update(mine_cells, ["is_mine"])

    @staticmethod
    def _calculate_adjacencies(cells):
        updates = []
        for cell in cells:
            if not cell.is_mine:
                cell.adjacent_mines = GameService._calculate_adjacent_mines(cell)
                updates.append(cell)
        Cell.objects.bulk_update(updates, ["adjacent_mines"])

    @staticmethod
    def _calculate_adjacent_mines(cell):
        neighbors = Cell.objects.get_neighbors(cell)
        return sum(1 for neighbor in neighbors if neighbor.is_mine)

    @staticmethod
    def _get_cell(game, row, column):
        try:
            return Cell.objects.get(game=game, row=row, column=column)
        except Cell.DoesNotExist:
            return None

    @staticmethod
    def reveal_cell(game, row, column):
        cell = GameService._get_cell(game, row, column)
        if not cell:
            return CELL_NOT_FOUND, HTTP_404_NOT_FOUND

        if cell.is_revealed:
            return CELL_ALREADY_REVEALED, HTTP_400_BAD_REQUEST

        if cell.is_mine:
            GameService._end_game(game, GameStatus.LOST)
            return GameSerializer(game).data, HTTP_200_OK

        GameService._reveal_cells(cell)

        if GameService._check_win_condition(game):
            GameService._end_game(game, GameStatus.WON)
            return GameSerializer(game).data, HTTP_200_OK

        return GameSerializer(game).data, HTTP_200_OK

    @staticmethod
    def _reveal_cells(cell):
        if cell.is_revealed:
            return
        cell.is_revealed = True
        cell.save()

        if cell.adjacent_mines == 0:
            neighbors = Cell.objects.get_neighbors(cell)
            for neighbor in neighbors:
                GameService._reveal_cells(neighbor)

    @staticmethod
    def _end_game(game, status):
        game.status = status
        game.finished_at = now()
        game.save()
        GameService._reveal_all_cells(game)

    @staticmethod
    def _reveal_all_cells(game):
        cells = Cell.objects.filter(game=game)
        with transaction.atomic():
            for cell in cells:
                cell.is_revealed = True
            Cell.objects.bulk_update(cells, ["is_revealed"])

    @staticmethod
    def _check_win_condition(game):
        return not Cell.objects.filter(
            game=game, is_revealed=False, is_mine=False
        ).exists()

    @staticmethod
    def toggle_flag(game, row, column):
        cell = GameService._get_cell(game, row, column)
        if not cell:
            return CELL_NOT_FOUND, HTTP_404_NOT_FOUND

        if cell.is_revealed:
            return CANNOT_FLAG_REVEALED_CELL, HTTP_400_BAD_REQUEST

        cell.is_flagged = not cell.is_flagged
        cell.save()

        return CellSerializer(cell).data, HTTP_200_OK
