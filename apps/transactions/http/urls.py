from django.urls import path

from . import views

app_name = "transactions_http"

urlpatterns = [
    path("", views.TransactionListView.as_view(), name="index"),
    path("create/", views.TransactionCreateView.as_view(), name="create"),
    path("<int:pk>/update/", views.TransactionUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.TransactionDeleteView.as_view(), name="delete"),
]
