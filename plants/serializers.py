from rest_framework import serializers
from .models import Plant, Family, Nursery, PlantType


class PlantTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantType
        fields = '__all__'


class FamilyListSerializer(serializers.ModelSerializer):
    plantsCount = serializers.IntegerField(source='plants.count', read_only=True)

    class Meta:
        model = Family
        fields = ['id', 'name', 'description', 'plantsCount']


class FamilyDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Family
        fields = '__all__'


class NurseryListSerializer(serializers.ModelSerializer):
    plantsCount = serializers.IntegerField(source='plants.count', read_only=True)

    class Meta:
        model = Nursery
        fields = ['id', 'name', 'location', 'contact_email', 'plantsCount']


class NurseryDetailSerializer(serializers.ModelSerializer):
    contactEmail = serializers.EmailField(source='contact_email', required=False, allow_null=True)

    class Meta:
        model = Nursery
        fields = ['id', 'name', 'location', 'contactEmail']


class PlantListSerializer(serializers.ModelSerializer):
    latinName = serializers.CharField(source='latin_name', read_only=True)
    imageUrl = serializers.CharField(source='image_url', read_only=True)
    lightLevel = serializers.CharField(source='light_level', read_only=True)
    petSafe = serializers.BooleanField(source='pet_safe', read_only=True)
    type = PlantTypeSerializer(read_only=True)
    family = FamilyDetailSerializer(read_only=True)
    nursery = NurseryDetailSerializer(read_only=True)

    class Meta:
        model = Plant
        fields = [
            'id', 'name', 'latinName', 'price', 'stock', 
            'imageUrl', 'lightLevel', 'difficulty', 'petSafe', 
            'type', 'family', 'nursery'
        ]


class PlantDetailSerializer(serializers.ModelSerializer):
    latinName = serializers.CharField(source='latin_name', read_only=True)
    imageUrl = serializers.CharField(source='image_url', read_only=True)
    lightLevel = serializers.CharField(source='light_level', read_only=True)
    petSafe = serializers.BooleanField(source='pet_safe', read_only=True)
    heightCm = serializers.IntegerField(source='height_cm', read_only=True)
    potDiameterCm = serializers.IntegerField(source='pot_diameter_cm', read_only=True)
    soldCount = serializers.IntegerField(source='sold_count', read_only=True)
    type = PlantTypeSerializer(read_only=True)
    family = FamilyDetailSerializer(read_only=True)
    nursery = NurseryDetailSerializer(read_only=True)

    class Meta:
        model = Plant
        fields = [
            'id', 'name', 'latinName', 'description', 'price', 'stock', 'soldCount',
            'imageUrl', 'lightLevel', 'watering', 'difficulty', 'petSafe',
            'heightCm', 'potDiameterCm', 'type', 'family', 'nursery',
            'created_at', 'updated_at'
        ]


class PlantCreateUpdateSerializer(serializers.ModelSerializer):
    latinName = serializers.CharField(source='latin_name', required=False, allow_blank=True, allow_null=True)
    imageUrl = serializers.URLField(source='image_url', required=False, allow_blank=True, allow_null=True)
    lightLevel = serializers.CharField(source='light_level', required=False)
    petSafe = serializers.BooleanField(source='pet_safe', required=False)
    heightCm = serializers.IntegerField(source='height_cm', required=False, allow_null=True)
    potDiameterCm = serializers.IntegerField(source='pot_diameter_cm', required=False, allow_null=True)
    typeId = serializers.PrimaryKeyRelatedField(queryset=PlantType.objects.all(), source='type')
    familyId = serializers.PrimaryKeyRelatedField(queryset=Family.objects.all(), source='family')
    nurseryId = serializers.PrimaryKeyRelatedField(queryset=Nursery.objects.all(), source='nursery')

    class Meta:
        model = Plant
        fields = [
            'name', 'latinName', 'description', 'price', 'stock',
            'imageUrl', 'lightLevel', 'watering', 'difficulty', 'petSafe',
            'heightCm', 'potDiameterCm', 'typeId', 'familyId', 'nurseryId'
        ]