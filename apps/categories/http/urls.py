from django.urls import path

from . import views

app_name = "categories_http"

urlpatterns = [
    path("", views.CategoryListView.as_view(), name="index"),
]
