from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from .constants import GAME_NOT_ACTIVE
from .models import Game
from .serializers import GameSerializer
from .services import GameService


class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def perform_create(self, serializer):
        game = serializer.save()
        GameService.initialize_cells(game)

    def _process_cell_action(self, request, cell_action):
        row = request.data.get("row")
        column = request.data.get("column")
        game = self.get_object()
        if not game.is_active():
            return GAME_NOT_ACTIVE, HTTP_400_BAD_REQUEST

        data, status_code = cell_action(game, row, column)

        return data, status_code

    @action(detail=True, methods=["post"])
    def flag(self, request, pk=None):
        data, status_code = self._process_cell_action(request, GameService.toggle_flag)
        return Response(data, status=status_code)

    @action(detail=True, methods=["post"])
    def reveal(self, request, pk=None):
        data, status_code = self._process_cell_action(request, GameService.reveal_cell)
        return Response(data, status=status_code)
