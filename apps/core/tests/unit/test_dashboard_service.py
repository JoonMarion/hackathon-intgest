from datetime import date
from decimal import Decimal

from apps.categories.models import Category
from apps.core.services.dashboard import DashboardService, DateRange
from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import CategoryFactory, TransactionFactory, UserFactory
from apps.transactions.models import Transaction


class DashboardServiceSummaryTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username='svc-user', email='svc-user@example.com')
        self.income_cat = CategoryFactory(
            user=self.user,
            kind=Category.Kind.INCOME,
            name='Salary',
        )
        self.expense_cat = CategoryFactory(
            user=self.user,
            kind=Category.Kind.EXPENSE,
            name='Food',
        )

    def test_get_summary_no_transactions(self):
        service = DashboardService(user=self.user)
        summary = service.get_summary()
        self.assertEqual(summary.total_income, Decimal('0'))
        self.assertEqual(summary.total_expense, Decimal('0'))
        self.assertEqual(summary.balance, Decimal('0'))

    def test_get_summary_with_transactions(self):
        TransactionFactory(
            user=self.user,
            category=self.income_cat,
            kind=Transaction.Kind.INCOME,
            amount='500.00',
            transaction_date=date(2026, 3, 10),
        )
        TransactionFactory(
            user=self.user,
            category=self.expense_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='200.00',
            transaction_date=date(2026, 3, 15),
        )
        service = DashboardService(user=self.user)
        summary = service.get_summary()
        self.assertEqual(summary.total_income, Decimal('500'))
        self.assertEqual(summary.total_expense, Decimal('200'))
        self.assertEqual(summary.balance, Decimal('300'))

    def test_get_summary_with_date_range(self):
        TransactionFactory(
            user=self.user,
            category=self.income_cat,
            kind=Transaction.Kind.INCOME,
            amount='100.00',
            transaction_date=date(2026, 1, 15),
        )
        TransactionFactory(
            user=self.user,
            category=self.income_cat,
            kind=Transaction.Kind.INCOME,
            amount='200.00',
            transaction_date=date(2026, 3, 15),
        )
        date_range = DateRange(date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
        service = DashboardService(user=self.user, date_range=date_range)
        summary = service.get_summary()
        self.assertEqual(summary.total_income, Decimal('200'))
        self.assertEqual(summary.total_expense, Decimal('0'))
        self.assertEqual(summary.balance, Decimal('200'))


class DashboardServiceHighlightsTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username='insight-user', email='insight-user@example.com')
        self.income_cat = CategoryFactory(
            user=self.user,
            kind=Category.Kind.INCOME,
            name='Salary',
        )
        self.expense_cat = CategoryFactory(
            user=self.user,
            kind=Category.Kind.EXPENSE,
            name='Home',
        )

    def test_get_highlights_returns_safe_dashboard_metrics(self):
        TransactionFactory(
            user=self.user,
            category=self.income_cat,
            kind=Transaction.Kind.INCOME,
            amount='1000.00',
            transaction_date=date(2026, 3, 10),
        )
        TransactionFactory(
            user=self.user,
            category=self.expense_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='400.00',
            description='Aluguel',
            transaction_date=date(2026, 3, 12),
        )
        TransactionFactory(
            user=self.user,
            category=self.expense_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='100.00',
            description='Mercado',
            transaction_date=date(2026, 3, 15),
        )

        service = DashboardService(user=self.user)
        highlights = service.get_highlights(summary=service.get_summary())

        self.assertEqual(highlights.transaction_count, 3)
        self.assertEqual(highlights.active_categories, 2)
        self.assertEqual(highlights.average_ticket, Decimal('500.00'))
        self.assertEqual(highlights.savings_rate, Decimal('50.0'))
        self.assertEqual(highlights.biggest_expense_label, 'Aluguel')
        self.assertEqual(highlights.biggest_expense_amount, Decimal('400.00'))

    def test_get_highlights_uses_category_name_when_description_is_blank(self):
        TransactionFactory(
            user=self.user,
            category=self.expense_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='300.00',
            description='',
            transaction_date=date(2026, 3, 18),
        )

        service = DashboardService(user=self.user)
        highlights = service.get_highlights(summary=service.get_summary())

        self.assertEqual(highlights.biggest_expense_label, 'Home')
        self.assertEqual(highlights.biggest_expense_amount, Decimal('300.00'))
        self.assertIsNone(highlights.savings_rate)


class DashboardServiceComparisonTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username='comparison-user', email='comparison-user@example.com')
        self.income_cat = CategoryFactory(user=self.user, kind=Category.Kind.INCOME, name='Salário')
        self.home_cat = CategoryFactory(user=self.user, kind=Category.Kind.EXPENSE, name='Moradia')
        self.food_cat = CategoryFactory(user=self.user, kind=Category.Kind.EXPENSE, name='Alimentação')
        self.date_range = DateRange(date_from=date(2026, 3, 11), date_to=date(2026, 3, 20))

    def test_get_period_comparison_computes_delta_absolute_and_percent(self):
        TransactionFactory(
            user=self.user,
            category=self.income_cat,
            kind=Transaction.Kind.INCOME,
            amount='1000.00',
            transaction_date=date(2026, 3, 12),
        )
        TransactionFactory(
            user=self.user,
            category=self.home_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='400.00',
            transaction_date=date(2026, 3, 12),
        )
        TransactionFactory(
            user=self.user,
            category=self.food_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='100.00',
            transaction_date=date(2026, 3, 14),
        )

        TransactionFactory(
            user=self.user,
            category=self.income_cat,
            kind=Transaction.Kind.INCOME,
            amount='800.00',
            transaction_date=date(2026, 3, 2),
        )
        TransactionFactory(
            user=self.user,
            category=self.home_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='300.00',
            transaction_date=date(2026, 3, 3),
        )

        service = DashboardService(user=self.user, date_range=self.date_range)
        comparison = service.get_period_comparison()

        self.assertEqual(comparison.income.current, Decimal('1000.00'))
        self.assertEqual(comparison.income.previous, Decimal('800.00'))
        self.assertEqual(comparison.income.delta_absolute, Decimal('200.00'))
        self.assertEqual(comparison.income.delta_percent, Decimal('25.0'))

        self.assertEqual(comparison.expense.current, Decimal('500.00'))
        self.assertEqual(comparison.expense.previous, Decimal('300.00'))
        self.assertEqual(comparison.expense.delta_absolute, Decimal('200.00'))
        self.assertEqual(comparison.expense.delta_percent, Decimal('66.7'))

        self.assertEqual(comparison.balance.current, Decimal('500.00'))
        self.assertEqual(comparison.balance.previous, Decimal('500.00'))
        self.assertEqual(comparison.balance.delta_absolute, Decimal('0.00'))
        self.assertEqual(comparison.balance.delta_percent, Decimal('0.0'))

    def test_get_period_comparison_handles_previous_zero(self):
        TransactionFactory(
            user=self.user,
            category=self.income_cat,
            kind=Transaction.Kind.INCOME,
            amount='900.00',
            transaction_date=date(2026, 3, 12),
        )

        service = DashboardService(user=self.user, date_range=self.date_range)
        comparison = service.get_period_comparison()

        self.assertEqual(comparison.income.delta_absolute, Decimal('900.00'))
        self.assertIsNone(comparison.income.delta_percent)


class DashboardServiceAdvancedInsightsTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username='advanced-user', email='advanced-user@example.com')
        self.income_cat = CategoryFactory(user=self.user, kind=Category.Kind.INCOME, name='Salário')
        self.home_cat = CategoryFactory(user=self.user, kind=Category.Kind.EXPENSE, name='Moradia')
        self.food_cat = CategoryFactory(user=self.user, kind=Category.Kind.EXPENSE, name='Alimentação')
        self.date_range = DateRange(date_from=date(2026, 3, 11), date_to=date(2026, 3, 20))

    def test_get_advanced_insights_returns_burn_runway_and_concentration(self):
        TransactionFactory(
            user=self.user,
            category=self.income_cat,
            kind=Transaction.Kind.INCOME,
            amount='1000.00',
            transaction_date=date(2026, 3, 12),
        )
        TransactionFactory(
            user=self.user,
            category=self.home_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='400.00',
            transaction_date=date(2026, 3, 12),
        )
        TransactionFactory(
            user=self.user,
            category=self.food_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='100.00',
            transaction_date=date(2026, 3, 14),
        )

        service = DashboardService(user=self.user, date_range=self.date_range)
        summary = service.get_summary()
        comparison = service.get_period_comparison()
        advanced = service.get_advanced_insights(summary=summary, comparison=comparison)

        self.assertEqual(advanced.burn_rate_daily, Decimal('50.00'))
        self.assertEqual(advanced.runway_days, Decimal('10.0'))
        self.assertEqual(advanced.top_expense_category, 'Moradia')
        self.assertEqual(advanced.top_expense_share_percent, Decimal('80.0'))
        self.assertIn('cobre aproximadamente', advanced.period_insight)

    def test_get_advanced_insights_with_no_expense(self):
        TransactionFactory(
            user=self.user,
            category=self.income_cat,
            kind=Transaction.Kind.INCOME,
            amount='700.00',
            transaction_date=date(2026, 3, 12),
        )

        service = DashboardService(user=self.user, date_range=self.date_range)
        advanced = service.get_advanced_insights(summary=service.get_summary())

        self.assertEqual(advanced.burn_rate_daily, Decimal('0.00'))
        self.assertIsNone(advanced.runway_days)
        self.assertIsNone(advanced.top_expense_category)
        self.assertIsNone(advanced.top_expense_share_percent)


class DashboardServiceChartTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username='chart-user', email='chart-user@example.com')

    def test_get_chart_data_default_range(self):
        service = DashboardService(user=self.user)
        chart = service.get_chart_data()
        self.assertIsInstance(chart.labels, list)
        self.assertEqual(len(chart.labels), 6)
        self.assertEqual(len(chart.income), 6)
        self.assertEqual(len(chart.expense), 6)

    def test_get_chart_data_with_date_range(self):
        date_range = DateRange(date_from=date(2026, 1, 1), date_to=date(2026, 3, 31))
        service = DashboardService(user=self.user, date_range=date_range)
        chart = service.get_chart_data()
        self.assertEqual(len(chart.labels), 3)
        self.assertIn('01/2026', chart.labels)
        self.assertIn('02/2026', chart.labels)
        self.assertIn('03/2026', chart.labels)

    def test_get_chart_data_swapped_dates(self):
        date_range = DateRange(date_from=date(2026, 4, 1), date_to=date(2026, 1, 1))
        service = DashboardService(user=self.user, date_range=date_range)
        chart = service.get_chart_data()
        self.assertTrue(len(chart.labels) > 0)
        self.assertIn('01/2026', chart.labels)
        self.assertIn('04/2026', chart.labels)


class DashboardServiceCategoryBreakdownTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(
            username='breakdown-user',
            email='breakdown-user@example.com',
        )
        self.food_cat = CategoryFactory(
            user=self.user,
            kind=Category.Kind.EXPENSE,
            name='Food',
        )
        self.transport_cat = CategoryFactory(
            user=self.user,
            kind=Category.Kind.EXPENSE,
            name='Transport',
        )

    def test_get_category_breakdown_expense(self):
        TransactionFactory(
            user=self.user,
            category=self.food_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='80.00',
            transaction_date=date(2026, 3, 10),
        )
        TransactionFactory(
            user=self.user,
            category=self.transport_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='40.00',
            transaction_date=date(2026, 3, 12),
        )
        service = DashboardService(user=self.user)
        breakdown = service.get_category_breakdown('expense')
        self.assertIn('Food', breakdown.labels)
        self.assertIn('Transport', breakdown.labels)
        food_index = breakdown.labels.index('Food')
        transport_index = breakdown.labels.index('Transport')
        self.assertEqual(breakdown.data[food_index], 80.0)
        self.assertEqual(breakdown.data[transport_index], 40.0)

    def test_get_category_breakdown_with_date_range(self):
        TransactionFactory(
            user=self.user,
            category=self.food_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='50.00',
            transaction_date=date(2026, 1, 10),
        )
        TransactionFactory(
            user=self.user,
            category=self.food_cat,
            kind=Transaction.Kind.EXPENSE,
            amount='30.00',
            transaction_date=date(2026, 3, 10),
        )
        date_range = DateRange(date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
        service = DashboardService(user=self.user, date_range=date_range)
        breakdown = service.get_category_breakdown('expense')
        self.assertEqual(breakdown.labels, ['Food'])
        self.assertEqual(breakdown.data, [30.0])


class DashboardServiceRecentTransactionsTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username='recent-user', email='recent-user@example.com')
        self.cat = CategoryFactory(
            user=self.user,
            kind=Category.Kind.EXPENSE,
            name='Misc',
        )

    def test_get_recent_transactions_returns_last_five(self):
        for index in range(7):
            TransactionFactory(
                user=self.user,
                category=self.cat,
                kind=Transaction.Kind.EXPENSE,
                amount='10.00',
                transaction_date=date(2026, 3, 1 + index),
            )
        service = DashboardService(user=self.user)
        recent = service.get_recent_transactions()
        self.assertEqual(len(recent), 5)
        dates = [transaction.transaction_date for transaction in recent]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_get_recent_transactions_with_date_range(self):
        TransactionFactory(
            user=self.user,
            category=self.cat,
            kind=Transaction.Kind.EXPENSE,
            amount='10.00',
            transaction_date=date(2026, 1, 5),
        )
        TransactionFactory(
            user=self.user,
            category=self.cat,
            kind=Transaction.Kind.EXPENSE,
            amount='20.00',
            transaction_date=date(2026, 3, 15),
        )
        date_range = DateRange(date_from=date(2026, 3, 1), date_to=date(2026, 3, 31))
        service = DashboardService(user=self.user, date_range=date_range)
        recent = service.get_recent_transactions()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].transaction_date, date(2026, 3, 15))


class DashboardServiceOrchestratorTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username='orch-user', email='orch-user@example.com')

    def test_get_dashboard_data_returns_all_sections(self):
        service = DashboardService(user=self.user)
        data = service.get_dashboard_data()
        self.assertIsNotNone(data.summary)
        self.assertIsNotNone(data.highlights)
        self.assertIsNotNone(data.comparison)
        self.assertIsNotNone(data.advanced_insights)
        self.assertIsNotNone(data.chart)
        self.assertIsNotNone(data.expense_breakdown)
        self.assertIsNotNone(data.income_breakdown)
        self.assertIsInstance(data.recent_transactions, list)
