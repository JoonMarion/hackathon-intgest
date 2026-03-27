from decimal import Decimal

from django.db.models import Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce

from apps.transactions.models import Transaction


def build_filtered_summary(queryset) -> dict[str, Decimal | int]:
    zero_amount = Value(
        Decimal("0.00"),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )
    summary = queryset.aggregate(
        transaction_count=Count("id"),
        income_count=Count("id", filter=Q(kind=Transaction.Kind.INCOME)),
        expense_count=Count("id", filter=Q(kind=Transaction.Kind.EXPENSE)),
        active_categories=Count("category_id", distinct=True),
        total_income=Coalesce(
            Sum("amount", filter=Q(kind=Transaction.Kind.INCOME)),
            zero_amount,
        ),
        total_expense=Coalesce(
            Sum("amount", filter=Q(kind=Transaction.Kind.EXPENSE)),
            zero_amount,
        ),
    )
    summary["net_total"] = summary["total_income"] - summary["total_expense"]
    return summary


def resolve_selected_category_name(categories, raw_category_id: str) -> str | None:
    if not raw_category_id.isdigit():
        return None

    selected_category = categories.filter(pk=raw_category_id).first()
    if selected_category is None:
        return None
    return selected_category.name