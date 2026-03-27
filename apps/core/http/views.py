import json
from dataclasses import asdict
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.core.services.dashboard import DashboardService, DateRange


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'core/pages/index.html'

    def _parse_date(self, param_name: str) -> date | None:
        value = self.request.GET.get(param_name, '').strip()
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    def _build_period_label(self, date_from: date | None, date_to: date | None) -> str:
        if date_from and date_to:
            return f'{date_from:%d/%m/%Y} - {date_to:%d/%m/%Y}'
        if date_from:
            return f'Desde {date_from:%d/%m/%Y}'
        if date_to:
            return f'Até {date_to:%d/%m/%Y}'
        return 'Todo o histórico'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        date_from = self._parse_date('date_from')
        date_to = self._parse_date('date_to')
        date_range = DateRange(date_from=date_from, date_to=date_to)

        service = DashboardService(user=self.request.user, date_range=date_range)
        data = service.get_dashboard_data()

        context['total_income'] = data.summary.total_income
        context['total_expense'] = data.summary.total_expense
        context['balance'] = data.summary.balance
        context['dashboard_highlights'] = data.highlights
        context['chart_labels'] = json.dumps(data.chart.labels)
        context['chart_income'] = json.dumps(data.chart.income)
        context['chart_expense'] = json.dumps(data.chart.expense)
        context['expense_categories_labels'] = json.dumps(data.expense_breakdown.labels)
        context['expense_categories_data'] = json.dumps(data.expense_breakdown.data)
        context['income_categories_labels'] = json.dumps(data.income_breakdown.labels)
        context['income_categories_data'] = json.dumps(data.income_breakdown.data)
        context['recent_transactions'] = data.recent_transactions
        context['current_filters'] = {
            'date_from': date_from.isoformat() if date_from else '',
            'date_to': date_to.isoformat() if date_to else '',
        }
        context['has_active_filters'] = bool(date_from or date_to)
        context['selected_period_label'] = self._build_period_label(date_from, date_to)
        context['top_expenses'] = json.dumps([asdict(expense) for expense in data.top_expenses])

        return context
