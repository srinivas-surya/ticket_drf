from rest_framework.routers import SimpleRouter
from rest_framework import routers

from . import viewsets
from django.urls import path


router = routers.SimpleRouter()

router.register(r'orders', viewsets.OrderViewSet)
urlpatterns = [
    path("events/",viewsets.EventViewSet.as_view(),name="event-list"),
    path("order_delete/<int:pk>/", viewsets.OrderDeletelApiView.as_view(), name="order-detail"),
    path("event_metric/<int:pk>/", viewsets.MetricDetailApiView.as_view(), name="event-metric")

]

urlpatterns += router.urls
