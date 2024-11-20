from random import sample

from django.db import transaction
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_200_OK

from .constants import CANNOT_FLAG_REVEALED_CELL, CELL_ALREADY_REVEALED, CELL_NOT_FOUND
from .models import Cell, GameStatus
from .serializers import GameSerializer, CellSerializer


class GameService:
    """Service class to handle game logic."""

    @staticmethod
    def initialize_cells(game):
        """
        Create the cells of the game, place the mines, and calculate adjacencies.

        Args:
            game (Game): The game instance for which cells are being initialized.
        """
        cells = GameService._create_cells(game)
        GameService._place_mines(game, cells)
        GameService._calculate_adjacencies(cells)

    @staticmethod
    def _create_cells(game):
        """
        Create game cells using bulk_create to optimize database access.

        Args:
            game (Game): The game instance for which cells are being created.

        Returns:
            QuerySet: A queryset of the created cells.
        """
        cells = [
            Cell(game=game, row=row, column=col)
            for row in range(game.rows)
            for col in range(game.columns)
        ]
        Cell.objects.bulk_create(cells)
        return Cell.objects.filter(game=game)

    @staticmethod
    def _place_mines(game, cells):
        """
        Randomly place mines in the game cells.

        Args:
            game (Game): The game instance for which mines are being placed.
            cells (QuerySet): The queryset of cells in the game.
        """
        mine_cells = sample(list(cells), game.mines)
        for mine in mine_cells:
            mine.is_mine = True
        Cell.objects.bulk_update(mine_cells, ["is_mine"])

    @staticmethod
    def _calculate_adjacencies(cells):
        """
        Calculate the number of adjacent mines for each cell.

        Args:
            cells (QuerySet): The queryset of cells in the game.
        """
        updates = []
        for cell in cells:
            if not cell.is_mine:
                cell.adjacent_mines = GameService._calculate_adjacent_mines(cell)
                updates.append(cell)
        Cell.objects.bulk_update(updates, ["adjacent_mines"])

    @staticmethod
    def _calculate_adjacent_mines(cell):
        """
        Calculate the number of mines adjacent to a given cell.

        Args:
            cell (Cell): The cell for which adjacent mines are being calculated.

        Returns:
            int: The number of adjacent mines.
        """
        neighbors = Cell.objects.get_neighbors(cell)
        return sum(1 for neighbor in neighbors if neighbor.is_mine)

    @staticmethod
    def _get_cell(game, row, column):
        """
        Retrieve a cell by its row and column in a given game.

        Args:
            game (Game): The game instance.
            row (int): The row number of the cell.
            column (int): The column number of the cell.

        Returns:
            Cell or None: The cell if found, otherwise None.
        """
        try:
            return Cell.objects.get(game=game, row=row, column=column)
        except Cell.DoesNotExist:
            return None

    @staticmethod
    def reveal_cell(game, row, column):
        """
        Reveal a cell and handle game logic for revealing cells.

        Args:
            game (Game): The game instance.
            row (int): The row number of the cell to reveal.
            column (int): The column number of the cell to reveal.

        Returns:
            tuple: A tuple containing the response data and HTTP status code.
        """
        cell = GameService._get_cell(game, row, column)
        if not cell:
            return CELL_NOT_FOUND, HTTP_404_NOT_FOUND

        if cell.is_revealed:
            return CELL_ALREADY_REVEALED, HTTP_400_BAD_REQUEST

        if cell.is_mine:
            GameService._end_game(game, GameStatus.LOST)
            return GameSerializer(game).data, HTTP_200_OK

        if cell.is_flagged:
            cell.toggle_flag()

        GameService._reveal_cells(cell)

        if GameService._check_win_condition(game):
            GameService._end_game(game, GameStatus.WON)
            return GameSerializer(game).data, HTTP_200_OK

        return GameSerializer(game).data, HTTP_200_OK

    @staticmethod
    def _reveal_cells(cell):
        """
        Recursively reveal cells starting from the given cell.

        Args:
            cell (Cell): The cell to start revealing from.
        """
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
        """
        End the game with a given status and reveal all cells.

        Args:
            game (Game): The game instance.
            status (GameStatus): The status to set for the game.
        """
        game.end_game(status)
        GameService._reveal_all_cells(game)

    @staticmethod
    def _reveal_all_cells(game):
        """
        Reveal all cells in the game.

        Args:
            game (Game): The game instance.
        """
        cells = Cell.objects.filter(game=game)
        with transaction.atomic():
            for cell in cells:
                cell.is_revealed = True
            Cell.objects.bulk_update(cells, ["is_revealed"])

    @staticmethod
    def _check_win_condition(game):
        """
        Check if the win condition is met for the game.

        Args:
            game (Game): The game instance.

        Returns:
            bool: True if the win condition is met, False otherwise.
        """
        return not Cell.objects.filter(
            game=game, is_revealed=False, is_mine=False
        ).exists()

    @staticmethod
    def toggle_flag(game, row, column):
        """
        Toggle the flag status of a cell.

        Args:
            game (Game): The game instance.
            row (int): The row number of the cell to flag/unflag.
            column (int): The column number of the cell to flag/unflag.

        Returns:
            tuple: A tuple containing the response data and HTTP status code.
        """
        cell = GameService._get_cell(game, row, column)
        if not cell:
            return CELL_NOT_FOUND, HTTP_404_NOT_FOUND

        if cell.is_revealed:
            return CANNOT_FLAG_REVEALED_CELL, HTTP_400_BAD_REQUEST

        cell.toggle_flag()

        return CellSerializer(cell).data, HTTP_200_OK
