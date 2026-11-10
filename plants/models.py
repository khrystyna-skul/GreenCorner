from django.db import models


class PlantType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Family(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Nursery(models.Model):
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.name


class Plant(models.Model):
    LIGHT_CHOICES = [
        ('low', 'Тінь / Розсіяне світло'),
        ('medium', 'Помірне світло'),
        ('high', 'Яскраве пряме світло'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Легкий'),
        ('medium', 'Середній'),
        ('hard', 'Складний'),
    ]

    name = models.CharField(max_length=150)
    latin_name = models.CharField(max_length=150, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    sold_count = models.PositiveIntegerField(default=0)
    image_url = models.URLField(blank=True, null=True)
    
    light_level = models.CharField(max_length=10, choices=LIGHT_CHOICES, default='medium')
    watering = models.CharField(max_length=100, blank=True, null=True)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
    pet_safe = models.BooleanField(default=True)
    
    height_cm = models.PositiveIntegerField(blank=True, null=True)
    pot_diameter_cm = models.PositiveIntegerField(blank=True, null=True)

    type = models.ForeignKey(PlantType, on_delete=models.PROTECT, related_name='plants')
    family = models.ForeignKey(Family, on_delete=models.PROTECT, related_name='plants')
    nursery = models.ForeignKey(Nursery, on_delete=models.PROTECT, related_name='plants')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name