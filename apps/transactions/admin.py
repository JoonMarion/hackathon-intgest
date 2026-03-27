from django.contrib import admin

from apps.transactions.models import DocumentFile, ExportJob, FinancialAccount, ImportJob, ImportRowResult, Transaction


@admin.register(FinancialAccount)
class FinancialAccountAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "name", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "user__username")


@admin.register(DocumentFile)
class DocumentFileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "purpose", "original_name", "size_bytes", "created_at")
    list_filter = ("purpose", "created_at")
    search_fields = ("original_name", "user__username")


@admin.register(ImportJob)
class ImportJobAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "imported_rows", "skipped_rows", "failed_rows", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "source_file__original_name")


@admin.register(ImportRowResult)
class ImportRowResultAdmin(admin.ModelAdmin):
    list_display = ("id", "import_job", "row_number", "status", "transaction", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("import_job__id", "message")


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "export_format", "status", "row_count", "created_at")
    list_filter = ("export_format", "status", "created_at")
    search_fields = ("user__username", "output_file__original_name")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "account",
        "category",
        "kind",
        "payee",
        "amount",
        "transaction_date",
        "created_at",
    )
    list_filter = ("kind", "transaction_date", "created_at")
    search_fields = ("description", "payee", "import_id")
