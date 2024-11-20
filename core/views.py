from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from .constants import GAME_NOT_ACTIVE
from .models import Game, GameStatus, GameMode
from .serializers import GameSerializer, LeaderboardGameSerializer
from .services import GameService


class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def perform_create(self, serializer):
        """Initialize the cells of the game after creation."""
        game = serializer.save()
        GameService.initialize_cells(game)

    def _process_cell_action(self, request, cell_action):
        """Process a cell action (flag or reveal) on a game."""
        row = request.data.get("row")
        column = request.data.get("column")
        game = self.get_object()
        if not game.is_active():
            return GAME_NOT_ACTIVE, HTTP_400_BAD_REQUEST

        data, status_code = cell_action(game, row, column)

        return data, status_code

    @action(detail=True, methods=["post"])
    def flag(self, request, pk=None):
        """Action to flag a cell in the game."""
        data, status_code = self._process_cell_action(request, GameService.toggle_flag)
        return Response(data, status=status_code)

    @action(detail=True, methods=["post"])
    def reveal(self, request, pk=None):
        """Action to reveal a cell in the game."""
        data, status_code = self._process_cell_action(request, GameService.reveal_cell)
        return Response(data, status=status_code)

    @action(detail=False, methods=["get"])
    def leaderboard(self, request):
        """
        Retrieve the leaderboard for each game mode order by the shortest duration.
        The number of top players returned can be controlled using the `size` query parameter.
        """
        size = int(request.query_params.get("size", 10))

        modes = [GameMode.EASY, GameMode.MEDIUM, GameMode.HARD, GameMode.CUSTOM]
        leaderboards = {}
        for mode in modes:
            leaderboard = Game.objects.filter(
                status=GameStatus.WON, mode=mode
            ).order_by("duration")[:size]
            leaderboards[mode] = LeaderboardGameSerializer(leaderboard, many=True).data

        return Response(leaderboards)
