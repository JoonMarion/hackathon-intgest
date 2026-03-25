import json
from datetime import date
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.views.generic import TemplateView

from apps.transactions.models import Transaction


def _month_range(start_date, end_date):
    """Generate (year, month) tuples from start to end inclusive."""
    current = start_date.replace(day=1)
    end = end_date.replace(day=1)
    while current <= end:
        yield current.year, current.month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/pages/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # 1. Summary totals
        income_total = (
            Transaction.objects.filter(user=user, kind="income").aggregate(
                total=Sum("amount")
            )["total"]
        ) or Decimal("0")
        expense_total = (
            Transaction.objects.filter(user=user, kind="expense").aggregate(
                total=Sum("amount")
            )["total"]
        ) or Decimal("0")

        context["total_income"] = income_total
        context["total_expense"] = expense_total
        context["balance"] = income_total - expense_total

        # 2. Monthly evolution (last 6 months)
        today = date.today()
        if today.month > 6:
            start_date = today.replace(month=today.month - 5, day=1)
        else:
            start_date = today.replace(
                year=today.year - 1, month=today.month + 7, day=1
            )

        monthly_data = (
            Transaction.objects.filter(user=user, transaction_date__gte=start_date)
            .annotate(month=TruncMonth("transaction_date"))
            .values("month", "kind")
            .annotate(total=Sum("amount"))
            .order_by("month")
        )

        monthly_map = {}
        for entry in monthly_data:
            key = (entry["month"].year, entry["month"].month)
            if key not in monthly_map:
                monthly_map[key] = {"income": Decimal("0"), "expense": Decimal("0")}
            monthly_map[key][entry["kind"]] = entry["total"]

        labels = []
        income_values = []
        expense_values = []
        for year, month in _month_range(start_date, today):
            labels.append(f"{month:02d}/{year}")
            data = monthly_map.get(
                (year, month), {"income": Decimal("0"), "expense": Decimal("0")}
            )
            income_values.append(float(data["income"]))
            expense_values.append(float(data["expense"]))

        context["chart_labels"] = json.dumps(labels)
        context["chart_income"] = json.dumps(income_values)
        context["chart_expense"] = json.dumps(expense_values)

        # 3. Category breakdown
        expense_by_cat = (
            Transaction.objects.filter(user=user, kind="expense")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )
        income_by_cat = (
            Transaction.objects.filter(user=user, kind="income")
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )

        context["expense_categories_labels"] = json.dumps(
            [e["category__name"] for e in expense_by_cat]
        )
        context["expense_categories_data"] = json.dumps(
            [float(e["total"]) for e in expense_by_cat]
        )
        context["income_categories_labels"] = json.dumps(
            [e["category__name"] for e in income_by_cat]
        )
        context["income_categories_data"] = json.dumps(
            [float(e["total"]) for e in income_by_cat]
        )

        # 4. Recent transactions
        context["recent_transactions"] = (
            Transaction.objects.filter(user=user)
            .select_related("category")
            .order_by("-transaction_date", "-created_at")[:5]
        )

        return context
