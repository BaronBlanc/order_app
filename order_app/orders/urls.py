from django.urls import path

from . import views

urlpatterns = [
    path("", views.OrderListView.as_view(), name="order_list"),
    path("<str:order_id>/", views.OrderDetailView.as_view(), name="order_by_id"),
]
