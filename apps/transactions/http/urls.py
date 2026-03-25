from django.urls import path

from . import views

app_name = "transactions_http"

urlpatterns = [
    path("", views.TransactionListView.as_view(), name="index"),
]
