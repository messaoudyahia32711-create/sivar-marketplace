from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Wilaya, Commune
from .serializers import WilayaSerializer, CommuneSerializer


class WilayaListView(APIView):
    """
    GET /api/localization/wilayas/
    جلب جميع الولايات مع أسعار التوصيل.
    """
    def get(self, request):
        wilayas = Wilaya.objects.all().order_by('code')
        serializer = WilayaSerializer(wilayas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CommuneListView(APIView):
    """
    GET /api/localization/communes/?wilaya_id=16
    جلب البلديات بناءً على رقم الولاية.
    """
    def get(self, request):
        wilaya_id = request.query_params.get('wilaya_id')
        
        if not wilaya_id:
            return Response(
                {"error": "يجب تقديم معرف الولاية (wilaya_id)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        communes = Commune.objects.filter(wilaya_id=wilaya_id).order_by('name')
        serializer = CommuneSerializer(communes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)