import logging
from django.db.models import Q, ProtectedError
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample

from plants.models import Plant, Family, Nursery, PlantType
from plants.serializers import (
    PlantListSerializer, PlantDetailSerializer, PlantCreateUpdateSerializer,
    FamilyListSerializer, FamilyDetailSerializer,
    NurseryListSerializer, NurseryDetailSerializer,
    PlantTypeSerializer
)

logger = logging.getLogger('plants')


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
    permission_classes = [IsAuthenticatedOrReadOnly]

    @extend_schema(
        tags=['Plants'],
        summary='Отримати список рослин',
        description='Повертає пагінований список кімнатних рослин із можливістю пошуку та сортування. Доступно всім користувачам без автентифікації.',
        parameters=[
            OpenApiParameter(name='search', description='Пошук за назвою, латинською назвою або родиною', required=False, type=str),
            OpenApiParameter(name='sort', description='Сортування: price_asc, price_desc, popularity', required=False, type=str),
            OpenApiParameter(name='page', description='Номер сторінки (за замовчуванням 1)', required=False, type=int),
            OpenApiParameter(name='limit', description='Кількість елементів на сторінці (за замовчуванням 12)', required=False, type=int),
        ],
        responses={200: PlantListSerializer(many=True)},
    )
    def get(self, request):
        qs = Plant.objects.all().select_related('type', 'family', 'nursery')

        search = request.query_params.get('search')
        sort = request.query_params.get('sort')
        logger.debug("Запит списку рослин (search=%r, sort=%r)", search, sort)

        if search:
            qs = qs.filter(
                Q(name__icontains=search) | 
                Q(latin_name__icontains=search) | 
                Q(family__name__icontains=search)
            )

        if sort == 'price_asc':
            qs = qs.order_by('price')
        elif sort == 'price_desc':
            qs = qs.order_by('-price')
        elif sort == 'popularity':
            qs = qs.order_by('-sold_count')
        else:
            qs = qs.order_by('-id')

        return paginate_queryset(qs, request, PlantListSerializer)

    @extend_schema(
        tags=['Plants'],
        summary='Створити нову рослину',
        description='Додає нову рослину до каталогу. Потрібен JWT access-токен у заголовку Authorization.',
        request=PlantCreateUpdateSerializer,
        responses={
            201: PlantDetailSerializer,
            400: {'description': 'Помилка валідації вхідних даних'},
            401: {'description': 'Користувач не автентифікований'},
        },
        examples=[
            OpenApiExample(
                name='Приклад створення монстери',
                value={
                    'name': 'Монстера',
                    'latinName': 'Monstera deliciosa',
                    'price': 450,
                    'stock': 12,
                    'lightLevel': 'medium',
                    'difficulty': 'easy',
                    'petSafe': False,
                    'typeId': 1,
                    'familyId': 1,
                    'nurseryId': 1,
                },
                request_only=True,
            )
        ],
    )
    def post(self, request):
        serializer = PlantCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            plant = serializer.save()
            logger.info(
                "Користувач '%s' створив рослину id=%s ('%s')",
                request.user.username, plant.id, plant.name
            )
            res_serializer = PlantDetailSerializer(plant)
            return Response(res_serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(
            "Помилка валідації при створенні рослини користувачем '%s': %s",
            request.user.username, serializer.errors
        )
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PlantDetailView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Plant.objects.select_related('type', 'family', 'nursery').get(pk=pk)
        except Plant.DoesNotExist:
            return None

    @extend_schema(
        tags=['Plants'],
        summary='Отримати детальну інформацію про рослину',
        description='Повертає повну інформацію про конкретну рослину за її ID. Доступно без автентифікації.',
        responses={
            200: PlantDetailSerializer,
            404: {'description': 'Рослину не знайдено'},
        },
    )
    def get(self, request, pk):
        plant = self.get_object(pk)
        if not plant:
            logger.warning("Запит деталей неіснуючої рослини id=%s", pk)
            return Response({'error': 'Рослину не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        logger.debug("Переглянуто деталі рослини id=%s ('%s')", plant.id, plant.name)
        serializer = PlantDetailSerializer(plant)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Plants'],
        summary='Оновити інформацію про рослину',
        description='Оновлює дані існуючої рослини за її ID. Потрібен JWT access-токен.',
        request=PlantCreateUpdateSerializer,
        responses={
            200: PlantDetailSerializer,
            400: {'description': 'Помилка валідації даних'},
            401: {'description': 'Користувач не автентифікований'},
            404: {'description': 'Рослину не знайдено'},
        },
    )
    def put(self, request, pk):
        plant = self.get_object(pk)
        if not plant:
            logger.warning("Спроба оновити неіснуючу рослину id=%s користувачем '%s'", pk, request.user.username)
            return Response({'error': 'Рослину не знайдено'}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlantCreateUpdateSerializer(plant, data=request.data)
        if serializer.is_valid():
            updated_plant = serializer.save()
            logger.info(
                "Користувач '%s' оновив рослину id=%s ('%s')",
                request.user.username, updated_plant.id, updated_plant.name
            )
            res_serializer = PlantDetailSerializer(updated_plant)
            return Response(res_serializer.data, status=status.HTTP_200_OK)

        logger.warning(
            "Помилка валідації при оновленні рослини id=%s користувачем '%s': %s",
            pk, request.user.username, serializer.errors
        )
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        tags=['Plants'],
        summary='Видалити рослину',
        description='Видаляє рослину з каталогу за її ID. Потрібен JWT access-токен.',
        responses={
            204: {'description': 'Рослину успішно видалено'},
            401: {'description': 'Користувач не автентифікований'},
            404: {'description': 'Рослину не знайдено'},
        },
    )
    def delete(self, request, pk):
        plant = self.get_object(pk)
        if not plant:
            logger.warning("Спроба видалити неіснуючу рослину id=%s користувачем '%s'", pk, request.user.username)
            return Response({'error': 'Рослину не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        plant_name = plant.name
        plant.delete()
        logger.info("Користувач '%s' видалив рослину id=%s ('%s')", request.user.username, pk, plant_name)
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
            logger.info("Створено родину рослин id=%s ('%s')", family.id, family.name)
            return Response(FamilyDetailSerializer(family).data, status=status.HTTP_201_CREATED)
        logger.warning("Помилка валідації при створенні родини: %s", serializer.errors)
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
            logger.info("Оновлено родину id=%s ('%s')", updated_family.id, updated_family.name)
            return Response(FamilyDetailSerializer(updated_family).data, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        family = self.get_object(pk)
        if not family:
            return Response({'error': 'Родину не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        try:
            family.delete()
            logger.info("Видалено родину id=%s", pk)
        except ProtectedError:
            logger.warning("Відхилено видалення родини id=%s через прив'язані рослини", pk)
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
            logger.info("Створено розсадник id=%s ('%s')", nursery.id, nursery.name)
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
            logger.info("Оновлено розсадник id=%s ('%s')", updated_nursery.id, updated_nursery.name)
            return Response(NurseryDetailSerializer(updated_nursery).data, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        nursery = self.get_object(pk)
        if not nursery:
            return Response({'error': 'Розсадник не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        try:
            nursery.delete()
            logger.info("Видалено розсадник id=%s", pk)
        except ProtectedError:
            logger.warning("Відхилено видалення розсадника id=%s через прив'язані рослини", pk)
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
            logger.info("Створено тип рослини id=%s ('%s')", ptype.id, ptype.name)
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
            logger.info("Оновлено тип рослини id=%s ('%s')", updated_type.id, updated_type.name)
            return Response(PlantTypeSerializer(updated_type).data, status=status.HTTP_200_OK)
        return Response({'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        ptype = self.get_object(pk)
        if not ptype:
            return Response({'error': 'Тип рослини не знайдено'}, status=status.HTTP_404_NOT_FOUND)
        try:
            ptype.delete()
            logger.info("Видалено тип рослини id=%s", pk)
        except ProtectedError:
            logger.warning("Відхилено видалення типу рослини id=%s через прив'язані рослини", pk)
            return Response({'error': 'Неможливо видалити тип, оскільки до нього прив’язані рослини'}, status=status.HTTP_409_CONFLICT)
        return Response(status=status.HTTP_204_NO_CONTENT)