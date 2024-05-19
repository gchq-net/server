from django.urls import path

from . import views

app_name = "logistics"

urlpatterns = [
    path("", views.LogisticsHomeView.as_view(), name="home"),
    path("planned-locations/", views.PlannedLocationsListView.as_view(), name="planned_list"),
    path("planned-locations/create/", views.PlannedLocationCreateView.as_view(), name="planned_create"),
    path("planned-locations/<uuid:pk>/", views.PlannedLocationEditView.as_view(), name="planned_edit"),
]
