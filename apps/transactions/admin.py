from django.contrib import admin

from apps.transactions.models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "category",
        "kind",
        "amount",
        "transaction_date",
        "created_at",
    )
    list_filter = ("kind", "transaction_date", "created_at")
    search_fields = ("description",)
