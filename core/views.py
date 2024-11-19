from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from .models import Game
from .serializers import GameSerializer
from .services import GameService


class GameViewSet(ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

    def perform_create(self, serializer):
        game = serializer.save()
        GameService.initialize_cells(game)

    @action(detail=True, methods=["post"])
    def flag(self, request, pk=None):
        row = request.data.get("row")
        column = request.data.get("column")
        game = self.get_object()

        if not game.is_active():
            return Response(
                {"error": "Game is not active"}, status=HTTP_400_BAD_REQUEST
            )

        data, success = GameService.toggle_flag(game, row, column)
        if not success:
            return Response(data, status=HTTP_400_BAD_REQUEST)

        return Response(data)

    @action(detail=True, methods=["post"])
    def reveal(self, request, pk=None):
        row = request.data.get("row")
        column = request.data.get("column")
        game = self.get_object()

        if not game.is_active():
            return Response(
                {"error": "Game is not active"}, status=HTTP_400_BAD_REQUEST
            )

        data, success = GameService.reveal_cell(game, row, column)
        if not success:
            return Response(data, status=HTTP_400_BAD_REQUEST)

        return Response(data)
