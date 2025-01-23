from .models import KYC,KYCDocument
from .serializer import KYCSerializer, KYCDocumentSerializer
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response

from rest_framework.decorators import action, api_view
from rest_framework.views import APIView


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class KYCViewSet(viewsets.ModelViewSet):
    queryset = KYC.objects.all()
    serializer_class = KYCSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        if self.request.user.is_staff:
            return KYC.objects.all() # Only Admin can see all KYC entries
        return KYC.objects.filter(User=self.request.user) # Regular users see their own KYC entries
    
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class KYCDocumentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    
    def get(self, request):
        kyc = KYC.objects.filter(user=request.user).first()
        if not kyc:
            return Response({"error": "KYC record not found for user."}, status=status.HTTP_404_NOT_FOUND)

        document = KYCDocument.objects.filter(kyc=kyc).first()
        if not document:
            return Response({"error": "No document found for this KYC record."}, status=status.HTTP_404_NOT_FOUND)

        serializer = KYCDocumentSerializer(document)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        print("POST request received")
        kyc = KYC.objects.filter(user=request.user).first()
        if not kyc:
            return Response({"error": "KYC record not found for user"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = KYCDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(kyc=kyc)
            return Response({"success": "Document uploaded successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)