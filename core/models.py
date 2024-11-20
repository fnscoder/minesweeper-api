from django.db import models
from django.utils.timezone import now


class GameStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    WON = "won", "Won"
    LOST = "lost", "Lost"


class GameMode(models.TextChoices):
    EASY = "easy", "Easy"
    MEDIUM = "medium", "Medium"
    HARD = "hard", "Hard"
    CUSTOM = "custom", "Custom"


class Game(models.Model):
    user = models.CharField(max_length=20, null=True, blank=True)
    rows = models.PositiveSmallIntegerField()
    columns = models.PositiveSmallIntegerField()
    mines = models.PositiveSmallIntegerField()
    status = models.CharField(
        max_length=10,
        choices=GameStatus.choices,
        default=GameStatus.ACTIVE,
    )
    mode = models.CharField(
        max_length=10,
        choices=GameMode.choices,
        default=GameMode.EASY,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration = models.FloatField(null=True, blank=True)

    def is_active(self):
        return self.status == GameStatus.ACTIVE

    def end_game(self, status):
        self.status = status
        self.finished_at = now()
        self.duration = (self.finished_at - self.created_at).total_seconds()
        self.save()

    def __str__(self):
        return f"Game {self.id}"


class CellManager(models.Manager):
    def get_neighbors(self, cell):
        return self.filter(
            game=cell.game,
            row__gte=cell.row - 1,
            row__lte=cell.row + 1,
            column__gte=cell.column - 1,
            column__lte=cell.column + 1,
        ).exclude(id=cell.id)


class Cell(models.Model):
    game = models.ForeignKey(Game, related_name="cells", on_delete=models.CASCADE)
    row = models.PositiveSmallIntegerField()
    column = models.PositiveSmallIntegerField()
    is_mine = models.BooleanField(default=False)
    is_revealed = models.BooleanField(default=False)
    is_flagged = models.BooleanField(default=False)
    adjacent_mines = models.IntegerField(default=0)

    objects = CellManager()

    def toggle_flag(self):
        """Toggle the flag status of the cell."""
        self.is_flagged = not self.is_flagged
        self.save()

    class Meta:
        unique_together = ("game", "row", "column")

    def __str__(self):
        return f"Cell {self.row}x{self.column} - Game {self.game.id}"
