from random import sample

from django.db import transaction
from django.utils.timezone import now
from .models import Cell, GameStatus


class GameService:
    @staticmethod
    def initialize_cells(game):
        cells = [
            Cell(game=game, row=row, column=col)
            for row in range(game.rows)
            for col in range(game.columns)
        ]
        Cell.objects.bulk_create(cells)

        all_cells = Cell.objects.filter(game=game)
        mine_cells = sample(list(all_cells), game.mines)
        for mine in mine_cells:
            mine.is_mine = True
            mine.save()

        for cell in all_cells:
            if not cell.is_mine:
                cell.adjacent_mines = GameService.calculate_adjacent_mines(cell)
                cell.save()

    @staticmethod
    def calculate_adjacent_mines(cell):
        neighbors = GameService.get_neighbors(cell)
        return sum(1 for neighbor in neighbors if neighbor.is_mine)

    @staticmethod
    def get_neighbors(cell):
        return Cell.objects.filter(
            game=cell.game,
            row__gte=cell.row - 1,
            row__lte=cell.row + 1,
            column__gte=cell.column - 1,
            column__lte=cell.column + 1,
        ).exclude(id=cell.id)

    @staticmethod
    def reveal_cell(game, row, column):
        try:
            cell = Cell.objects.get(game=game, row=row, column=column)
        except Cell.DoesNotExist:
            return {"error": "Cell not found"}, False

        if cell.is_revealed:
            return {"error": "Cell already revealed"}, False

        if cell.is_mine:
            GameService.end_game(game, GameStatus.LOST)
            return GameService.serialize_game(game), True

        GameService.reveal_cells(cell)

        if GameService.check_win_condition(game):
            GameService.end_game(game, GameStatus.WON)
            return GameService.serialize_game(game), True

        return GameService.serialize_game(game), True

    @staticmethod
    def reveal_cells(cell):
        if cell.is_revealed:
            return
        cell.is_revealed = True
        cell.save()

        if cell.adjacent_mines == 0:
            neighbors = GameService.get_neighbors(cell)
            for neighbor in neighbors:
                GameService.reveal_cells(neighbor)

    @staticmethod
    def end_game(game, status):
        game.status = status
        game.finished_at = now()
        game.save()
        GameService.reveal_all_cells(game)

    @staticmethod
    def reveal_all_cells(game):
        cells = Cell.objects.filter(game=game)
        with transaction.atomic():
            for cell in cells:
                cell.is_revealed = True
                cell.save()

    @staticmethod
    def check_win_condition(game):
        return not Cell.objects.filter(
            game=game, is_revealed=False, is_mine=False
        ).exists()

    @staticmethod
    def toggle_flag(game, row, column):
        try:
            cell = Cell.objects.get(game=game, row=row, column=column)
        except Cell.DoesNotExist:
            return {"error": "Cell not found"}, False

        if cell.is_revealed:
            return {"error": "Cannot flag a revealed cell"}, False

        cell.is_flagged = not cell.is_flagged
        cell.save()

        return {
            "success": f"Cell at ({row}, {column}) {'flagged' if cell.is_flagged else 'unflagged'}."
        }, True

    @staticmethod
    def serialize_game(game):
        from .serializers import GameSerializer

        return GameSerializer(game).data
