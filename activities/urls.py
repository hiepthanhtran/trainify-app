from django.urls import path, include
from rest_framework import routers

from activities import views

router = routers.DefaultRouter()
router.register("activities", views.ActivityViewSet, basename="activities")
router.register("deficiency-reports", views.DeficiencyReportViewSet, basename="deficiency-reports")

urlpatterns = [
    path("", include(router.urls)),
    path('attendance/', views.AttendanceViewSet.as_view(), name='attendance'),
]
