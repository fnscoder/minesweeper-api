from rest_framework import serializers

from .constants import MINES_MUST_BE_SMALLER_THAN_CELLS
from .models import Game, Cell, GameMode


GAME_CONFIG = {
    "easy": {"rows": 9, "columns": 9, "mines": 10},
    "medium": {"rows": 16, "columns": 16, "mines": 40},
    "hard": {"rows": 30, "columns": 16, "mines": 99},
}


class CellSerializer(serializers.ModelSerializer):
    adjacent_mines = serializers.SerializerMethodField()

    class Meta:
        model = Cell
        fields = (
            "id",
            "row",
            "column",
            "is_revealed",
            "is_flagged",
            "is_mine",
            "adjacent_mines",
        )
        extra_kwargs = {
            "is_mine": {"write_only": True},
        }

    def get_adjacent_mines(self, obj):
        """Return the number of adjacent mines only if the cell is revealed."""
        if obj.is_revealed:
            return obj.adjacent_mines
        return None


class GameSerializer(serializers.ModelSerializer):
    duration = serializers.SerializerMethodField()
    rows = serializers.IntegerField(min_value=1, allow_null=True, required=False)
    columns = serializers.IntegerField(min_value=1, allow_null=True, required=False)
    mines = serializers.IntegerField(min_value=1, allow_null=True, required=False)
    cells = CellSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = "__all__"
        read_only_fields = (
            "id",
            "status",
            "created_at",
            "updated_at",
            "finished_at",
            "cells",
            "duration",
        )

    def get_duration(self, obj):
        return obj.duration

    def validate(self, data):
        mode = data.get("mode")
        if mode != GameMode.CUSTOM:
            data.update(GAME_CONFIG[mode])
            return data

        rows = data.get("rows")
        columns = data.get("columns")
        mines = data.get("mines")
        if mines >= rows * columns:
            raise serializers.ValidationError(
                {"mines": MINES_MUST_BE_SMALLER_THAN_CELLS}
            )
        return data
