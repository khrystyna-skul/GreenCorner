from django.urls import path
from .views import (
    PlantListCreateView, PlantDetailView,
    FamilyListCreateView, FamilyDetailView, FamilyPlantsView,
    NurseryListCreateView, NurseryDetailView, NurseryPlantsView,
    PlantTypeListCreateView, PlantTypeDetailView
)

urlpatterns = [
    path('plants/', PlantListCreateView.as_view(), name='plant-list-create'),
    path('plants/<int:pk>/', PlantDetailView.as_view(), name='plant-detail'),

    path('families/', FamilyListCreateView.as_view(), name='family-list-create'),
    path('families/<int:pk>/', FamilyDetailView.as_view(), name='family-detail'),
    path('families/<int:pk>/plants/', FamilyPlantsView.as_view(), name='family-plants'),

    path('nurseries/', NurseryListCreateView.as_view(), name='nursery-list-create'),
    path('nurseries/<int:pk>/', NurseryDetailView.as_view(), name='nursery-detail'),
    path('nurseries/<int:pk>/plants/', NurseryPlantsView.as_view(), name='nursery-plants'),

    path('plant-types/', PlantTypeListCreateView.as_view(), name='plant-type-list-create'),
    path('plant-types/<int:pk>/', PlantTypeDetailView.as_view(), name='plant-type-detail'),
]