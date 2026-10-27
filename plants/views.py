from django.db.models import Q, ProtectedError
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Plant, Family, Nursery, PlantType
from .serializers import (
    PlantListSerializer, PlantDetailSerializer, PlantCreateUpdateSerializer,
    FamilyListSerializer, FamilyDetailSerializer,
    NurseryListSerializer, NurseryDetailSerializer,
    PlantTypeSerializer
)


def paginate_queryset(queryset, request, serializer_class):
    page_number = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 12))

    paginator = Paginator(queryset, limit)
    page_obj = paginator.get_page(page_number)

    serializer = serializer_class(page_obj.object_list, many=True)
    return Response({
        'items': serializer.data,
        'page': page_number,
        'limit': limit,
        'total': paginator.count
    }, status=status.HTTP_200_OK)



class PlantListCreateView(APIView):
    def get(self, request):
        qs = Plant.objects.all().select_related('type', 'family', 'nursery')

        search = request.query_params.get('search')
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | 
                Q(latin_name__icontains=search) | 
                Q(family__name__icontains=search)
            )

        sort = request.query_params.get('sort')
        if sort == 'price_asc':
            qs = qs.order_by('price')
        elif sort == 'price_desc':
            qs = qs.order_by('-price')
        elif sort == 'popularity':
            qs = qs.order_by('-sold_count')
        else:
            qs = qs.order_by('-id')

        return paginate_queryset(qs, request, PlantListSerializer)

    def post(self, request):
        serializer = PlantCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            plant = serializer.save()
            res_serializer = PlantDetailSerializer(plant)
            return Response(res_serializer.data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PlantDetailView(APIView):
    def get_object(self, pk):
        try:
            return Plant.objects.select_related('type', 'family', 'nursery').get(pk=pk)
        except Plant.DoesNotExist:
            return None

    def get(self, request, pk):
        plant = self.get_object(pk)
        if not plant:
            return Response({'error': 'Рослину не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlantDetailSerializer(plant)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        plant = self.get_object(pk)
        if not plant:
            return Response({'error': 'Рослину не знайдено'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlantCreateUpdateSerializer(plant, data=request.data)
        if serializer.is_valid():
            updated_plant = serializer.save()
            res_serializer = PlantDetailSerializer(updated_plant)
            return Response(res_serializer.data, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        plant = self.get_object(pk)
        if not plant:
            return Response({'error': 'Рослину не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        plant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



class FamilyListCreateView(APIView):
    def get(self, request):
        families = Family.objects.all().prefetch_related('plants')
        serializer = FamilyListSerializer(families, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FamilyDetailSerializer(data=request.data)
        if serializer.is_valid():
            family = serializer.save()
            return Response(FamilyDetailSerializer(family).data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class FamilyDetailView(APIView):
    def get_object(self, pk):
        try:
            return Family.objects.get(pk=pk)
        except Family.DoesNotExist:
            return None

    def get(self, request, pk):
        family = self.get_object(pk)
        if not family:
            return Response({'error': 'Родину не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        return Response(FamilyDetailSerializer(family).data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        family = self.get_object(pk)
        if not family:
            return Response({'error': 'Родину не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        serializer = FamilyDetailSerializer(family, data=request.data)
        if serializer.is_valid():
            updated_family = serializer.save()
            return Response(FamilyDetailSerializer(updated_family).data, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        family = self.get_object(pk)
        if not family:
            return Response({'error': 'Родину не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        try:
            family.delete()
        except ProtectedError:
            return Response({'error': 'Неможливо видалити родину, оскільки до неї прив’язані рослини'}, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FamilyPlantsView(APIView):
    def get(self, request, pk):
        if not Family.objects.filter(pk=pk).exists():
            return Response({'error': 'Родину не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        qs = Plant.objects.filter(family_id=pk).select_related('type', 'family', 'nursery')
        return paginate_queryset(qs, request, PlantListSerializer)



class NurseryListCreateView(APIView):
    def get(self, request):
        nurseries = Nursery.objects.all().prefetch_related('plants')
        serializer = NurseryListSerializer(nurseries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = NurseryDetailSerializer(data=request.data)
        if serializer.is_valid():
            nursery = serializer.save()
            return Response(NurseryDetailSerializer(nursery).data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class NurseryDetailView(APIView):
    def get_object(self, pk):
        try:
            return Nursery.objects.get(pk=pk)
        except Nursery.DoesNotExist:
            return None

    def get(self, request, pk):
        nursery = self.get_object(pk)
        if not nursery:
            return Response({'error': 'Розсадник не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        return Response(NurseryDetailSerializer(nursery).data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        nursery = self.get_object(pk)
        if not nursery:
            return Response({'error': 'Розсадник не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        serializer = NurseryDetailSerializer(nursery, data=request.data)
        if serializer.is_valid():
            updated_nursery = serializer.save()
            return Response(NurseryDetailSerializer(updated_nursery).data, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        nursery = self.get_object(pk)
        if not nursery:
            return Response({'error': 'Розсадник не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        try:
            nursery.delete()
        except ProtectedError:
            return Response({'error': 'Неможливо видалити розсадник, оскільки до нього прив’язані рослини'}, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)


class NurseryPlantsView(APIView):
    def get(self, request, pk):
        if not Nursery.objects.filter(pk=pk).exists():
            return Response({'error': 'Розсадник не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        qs = Plant.objects.filter(nursery_id=pk).select_related('type', 'family', 'nursery')
        return paginate_queryset(qs, request, PlantListSerializer)


class PlantTypeListCreateView(APIView):
    def get(self, request):
        types = PlantType.objects.all()
        serializer = PlantTypeSerializer(types, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PlantTypeSerializer(data=request.data)
        if serializer.is_valid():
            ptype = serializer.save()
            return Response(PlantTypeSerializer(ptype).data, status=status.HTTP_201_CREATED)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PlantTypeDetailView(APIView):
    def get_object(self, pk):
        try:
            return PlantType.objects.get(pk=pk)
        except PlantType.DoesNotExist:
            return None

    def put(self, request, pk):
        ptype = self.get_object(pk)
        if not ptype:
            return Response({'error': 'Тип рослини не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlantTypeSerializer(ptype, data=request.data)
        if serializer.is_valid():
            updated_type = serializer.save()
            return Response(PlantTypeSerializer(updated_type).data, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ptype = self.get_object(pk)
        if not ptype:
            return Response({'error': 'Тип рослини не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        try:
            ptype.delete()
        except ProtectedError:
            return Response({'error': 'Неможливо видалити тип, оскільки до нього прив’язані рослини'}, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)