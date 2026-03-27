from django.urls import path

from . import views

app_name = "transactions_http"

urlpatterns = [
    path("", views.TransactionListView.as_view(), name="index"),
    path("create/", views.TransactionCreateView.as_view(), name="create"),
    path("<int:pk>/update/", views.TransactionUpdateView.as_view(), name="update"),
    path("<int:pk>/delete/", views.TransactionDeleteView.as_view(), name="delete"),
    path("importar/", views.TransactionImportUploadView.as_view(), name="import_upload"),
    path("importacoes/<int:pk>/mapeamento/", views.TransactionImportMappingView.as_view(), name="import_mapping"),
    path("importacoes/<int:pk>/preview/", views.TransactionImportPreviewView.as_view(), name="import_preview"),
    path("importacoes/<int:pk>/confirmar/", views.TransactionImportConfirmView.as_view(), name="import_confirm"),
    path("importacoes/<int:pk>/status/", views.TransactionImportStatusView.as_view(), name="import_status"),
    path("exportar/", views.TransactionExportCreateView.as_view(), name="export_create"),
    path("exportacoes/<int:pk>/", views.TransactionExportStatusView.as_view(), name="export_status"),
    path("exportacoes/<int:pk>/download/", views.TransactionExportDownloadView.as_view(), name="export_download"),
]
