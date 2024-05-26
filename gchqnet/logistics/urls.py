from django.urls import path

from . import views

app_name = "logistics"

urlpatterns = [
    path("", views.LogisticsHomeView.as_view(), name="home"),
    path("planned-locations/", views.PlannedLocationsListView.as_view(), name="planned_list"),
    path("planned-locations/map/", views.PlannedLocationMapView.as_view(), name="planned_map"),
    path("planned-locations/create/", views.PlannedLocationCreateView.as_view(), name="planned_create"),
    path("planned-locations/<uuid:pk>/", views.PlannedLocationEditView.as_view(), name="planned_edit"),
    path("planned-locations/<uuid:pk>/delete/", views.PlannedLocationDeleteView.as_view(), name="planned_delete"),
]
