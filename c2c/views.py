from rest_framework import viewsets, permissions, status
from .models import Trade
from .serializer import TradeSerializer
from rest_framework.decorators import permission_classes, action
from rest_framework.response import Response


class TradeViewSet(viewsets.ModelViewSet):
    queryset = Trade.objects.all()
    serializer_class = TradeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Trade.objects.filter(status="open")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def completed_trade(self, request, pk=None):
        """
        
        Custom ViewSet action to get all completed trade
        """
        trade = self.get_object() #Get tge specific trade instance
        if trade.status != 'open':
            return Response({"detail": "Trade is already completed or closed."}, status=status.HTTP_400_BAD_REQUEST)
        
        # update the trade status to closed
        trade.status = 'closed'
        trade.save()

        return Response({"detail": "Trade completed successfully."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def completed_history(self, request):
        trade = Trade.objects.filter(status="closed")
        serializer = TradeSerializer(trade, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
