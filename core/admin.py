from django.contrib import admin

from .models import Game, Cell


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "mode")


@admin.register(Cell)
class CellAdmin(admin.ModelAdmin):
    list_display = (
        "row",
        "column",
        "is_revealed",
        "is_flagged",
        "is_mine",
        "adjacent_mines",
    )
