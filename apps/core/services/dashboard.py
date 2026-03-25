from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncMonth

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


@dataclass(frozen=True)
class DateRange:
    date_from: date | None = None
    date_to: date | None = None


@dataclass(frozen=True)
class DashboardSummary:
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal


@dataclass(frozen=True)
class ChartData:
    labels: list[str]
    income: list[float]
    expense: list[float]


@dataclass(frozen=True)
class CategoryBreakdown:
    labels: list[str]
    data: list[float]


@dataclass(frozen=True)
class DashboardData:
    summary: DashboardSummary
    chart: ChartData
    expense_breakdown: CategoryBreakdown
    income_breakdown: CategoryBreakdown
    recent_transactions: list


class DashboardService:
    def __init__(self, user, date_range: DateRange | None = None):
        self._user = user
        self._date_range = date_range or DateRange()

    def _base_queryset(self):
        """Return user-scoped queryset with optional date range filter."""
        qs = Transaction.objects.filter(user=self._user)
        if self._date_range.date_from:
            qs = qs.filter(transaction_date__gte=self._date_range.date_from)
        if self._date_range.date_to:
            qs = qs.filter(transaction_date__lte=self._date_range.date_to)
        return qs

    def get_summary(self) -> DashboardSummary:
        qs = self._base_queryset()
        totals_by_kind = {
            row["kind"]: row["total"]
            for row in qs.values("kind").annotate(total=Sum("amount"))
        }
        income_total = totals_by_kind.get("income", Decimal("0"))
        expense_total = totals_by_kind.get("expense", Decimal("0"))
        return DashboardSummary(
            total_income=income_total,
            total_expense=expense_total,
            balance=income_total - expense_total,
        )

    def _get_chart_range(self) -> tuple[date, date]:
        """Determine the date range for chart labels."""
        today = date.today()

        effective_from = self._date_range.date_from
        effective_to = self._date_range.date_to

        # Swap if inverted
        if effective_from and effective_to and effective_to < effective_from:
            effective_from, effective_to = effective_to, effective_from

        if effective_from and effective_to:
            return effective_from, effective_to
        elif effective_from:
            return effective_from, today
        elif effective_to:
            # Default to 6 months before date_to
            if effective_to.month > 6:
                start = effective_to.replace(month=effective_to.month - 5, day=1)
            else:
                start = effective_to.replace(
                    year=effective_to.year - 1, month=effective_to.month + 7, day=1
                )
            return start, effective_to
        else:
            # Default: last 6 months
            if today.month > 6:
                start = today.replace(month=today.month - 5, day=1)
            else:
                start = today.replace(
                    year=today.year - 1, month=today.month + 7, day=1
                )
            return start, today

    def get_chart_data(self) -> ChartData:
        chart_start, chart_end = self._get_chart_range()

        qs = Transaction.objects.filter(
            user=self._user,
            transaction_date__gte=chart_start,
            transaction_date__lte=chart_end,
        )

        monthly_data = (
            qs.annotate(month=TruncMonth("transaction_date"))
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
        for year, month in _month_range(chart_start, chart_end):
            labels.append(f"{month:02d}/{year}")
            data = monthly_map.get(
                (year, month), {"income": Decimal("0"), "expense": Decimal("0")}
            )
            income_values.append(float(data["income"]))
            expense_values.append(float(data["expense"]))

        return ChartData(labels=labels, income=income_values, expense=expense_values)

    def get_category_breakdown(self, kind: str) -> CategoryBreakdown:
        breakdown = (
            self._base_queryset()
            .filter(kind=kind)
            .values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")
        )
        return CategoryBreakdown(
            labels=[entry["category__name"] for entry in breakdown],
            data=[float(entry["total"]) for entry in breakdown],
        )

    def get_recent_transactions(self, limit: int = 5):
        return (
            self._base_queryset()
            .select_related("category")
            .order_by("-transaction_date", "-created_at")[:limit]
        )

    def get_dashboard_data(self) -> DashboardData:
        return DashboardData(
            summary=self.get_summary(),
            chart=self.get_chart_data(),
            expense_breakdown=self.get_category_breakdown("expense"),
            income_breakdown=self.get_category_breakdown("income"),
            recent_transactions=list(self.get_recent_transactions()),
        )
