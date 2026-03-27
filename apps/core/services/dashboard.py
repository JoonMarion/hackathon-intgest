from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.db.models import Avg, Count, Sum
from django.db.models.functions import TruncMonth

from apps.transactions.models import Transaction


def _month_range(start_date: date, end_date: date):
    current = start_date.replace(day=1)
    end = end_date.replace(day=1)
    while current <= end:
        yield current.year, current.month
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)


def _start_months_before(reference_date: date, months_back: int) -> date:
    year = reference_date.year
    month = reference_date.month - months_back
    while month <= 0:
        year -= 1
        month += 12
    return date(year, month, 1)


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
class DashboardHighlights:
    transaction_count: int
    active_categories: int
    average_ticket: Decimal
    savings_rate: Decimal | None
    biggest_expense_label: str | None
    biggest_expense_amount: Decimal | None


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
class TopExpense:
    description: str
    amount: float
    category_name: str
    date: str


@dataclass(frozen=True)
class DashboardData:
    summary: DashboardSummary
    highlights: DashboardHighlights
    chart: ChartData
    expense_breakdown: CategoryBreakdown
    income_breakdown: CategoryBreakdown
    recent_transactions: list
    top_expenses: list[TopExpense]


class DashboardService:
    def __init__(self, user, date_range: DateRange | None = None):
        self._user = user
        self._date_range = date_range or DateRange()

    def _base_queryset(self):
        qs = Transaction.objects.filter(user=self._user)
        if self._date_range.date_from:
            qs = qs.filter(transaction_date__gte=self._date_range.date_from)
        if self._date_range.date_to:
            qs = qs.filter(transaction_date__lte=self._date_range.date_to)
        return qs

    def get_summary(self) -> DashboardSummary:
        qs = self._base_queryset()
        totals_by_kind = {
            row['kind']: row['total']
            for row in qs.values('kind').annotate(total=Sum('amount'))
        }
        income_total = totals_by_kind.get('income', Decimal('0'))
        expense_total = totals_by_kind.get('expense', Decimal('0'))
        return DashboardSummary(
            total_income=income_total,
            total_expense=expense_total,
            balance=income_total - expense_total,
        )

    def get_highlights(self, summary: DashboardSummary | None = None) -> DashboardHighlights:
        qs = self._base_queryset()
        aggregate = qs.aggregate(
            transaction_count=Count('id'),
            active_categories=Count('category_id', distinct=True),
            average_ticket=Avg('amount'),
        )
        summary = summary or self.get_summary()
        biggest_expense = (
            qs.filter(kind='expense')
            .select_related('category')
            .order_by('-amount', '-transaction_date')
            .first()
        )

        average_ticket = aggregate['average_ticket'] or Decimal('0')
        average_ticket = average_ticket.quantize(
            Decimal('0.01'),
            rounding=ROUND_HALF_UP,
        )

        savings_rate = None
        if summary.total_income > 0:
            savings_rate = ((summary.balance / summary.total_income) * Decimal('100')).quantize(
                Decimal('0.1'),
                rounding=ROUND_HALF_UP,
            )

        biggest_expense_label = None
        biggest_expense_amount = None
        if biggest_expense is not None:
            biggest_expense_label = biggest_expense.description or biggest_expense.category.name
            biggest_expense_amount = biggest_expense.amount.quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP,
            )

        return DashboardHighlights(
            transaction_count=aggregate['transaction_count'] or 0,
            active_categories=aggregate['active_categories'] or 0,
            average_ticket=average_ticket,
            savings_rate=savings_rate,
            biggest_expense_label=biggest_expense_label,
            biggest_expense_amount=biggest_expense_amount,
        )

    def _get_chart_range(self) -> tuple[date, date]:
        today = date.today()
        effective_from = self._date_range.date_from
        effective_to = self._date_range.date_to

        if effective_from and effective_to and effective_to < effective_from:
            effective_from, effective_to = effective_to, effective_from

        if effective_from and effective_to:
            return effective_from, effective_to
        if effective_from:
            return effective_from, today
        if effective_to:
            return _start_months_before(effective_to, 5), effective_to
        return _start_months_before(today, 5), today

    def get_chart_data(self) -> ChartData:
        chart_start, chart_end = self._get_chart_range()
        qs = Transaction.objects.filter(
            user=self._user,
            transaction_date__gte=chart_start,
            transaction_date__lte=chart_end,
        )
        monthly_data = (
            qs.annotate(month=TruncMonth('transaction_date'))
            .values('month', 'kind')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        monthly_map = {}
        for entry in monthly_data:
            key = (entry['month'].year, entry['month'].month)
            if key not in monthly_map:
                monthly_map[key] = {'income': Decimal('0'), 'expense': Decimal('0')}
            monthly_map[key][entry['kind']] = entry['total']

        labels = []
        income_values = []
        expense_values = []
        for year, month in _month_range(chart_start, chart_end):
            labels.append(f'{month:02d}/{year}')
            data = monthly_map.get(
                (year, month),
                {'income': Decimal('0'), 'expense': Decimal('0')},
            )
            income_values.append(float(data['income']))
            expense_values.append(float(data['expense']))

        return ChartData(labels=labels, income=income_values, expense=expense_values)

    def get_category_breakdown(self, kind: str) -> CategoryBreakdown:
        breakdown = (
            self._base_queryset()
            .filter(kind=kind)
            .values('category__name')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )
        return CategoryBreakdown(
            labels=[entry['category__name'] for entry in breakdown],
            data=[float(entry['total']) for entry in breakdown],
        )

    def get_recent_transactions(self, limit: int = 5):
        return (
            self._base_queryset()
            .select_related('category')
            .order_by('-transaction_date', '-created_at')[:limit]
        )

    def get_top_expenses(self, limit: int = 5) -> list[TopExpense]:
        qs = (
            self._base_queryset()
            .filter(kind='expense')
            .select_related('category')
            .order_by('-amount', '-transaction_date')[:limit]
        )
        return [
            TopExpense(
                description=t.description or 'Sem descrição',
                amount=float(t.amount),
                category_name=t.category.name,
                date=t.transaction_date.isoformat(),
            )
            for t in qs
        ]

    def get_dashboard_data(self) -> DashboardData:
        summary = self.get_summary()
        return DashboardData(
            summary=summary,
            highlights=self.get_highlights(summary=summary),
            chart=self.get_chart_data(),
            expense_breakdown=self.get_category_breakdown('expense'),
            income_breakdown=self.get_category_breakdown('income'),
            recent_transactions=list(self.get_recent_transactions()),
            top_expenses=self.get_top_expenses(),
        )
