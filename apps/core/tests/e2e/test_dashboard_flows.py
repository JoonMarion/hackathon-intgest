import re
from datetime import date

from playwright.sync_api import expect

from apps.categories.models import Category
from apps.core.tests.e2e.base import PlaywrightE2EBaseTestCase
from apps.core.tests.factories import CategoryFactory, TransactionFactory, UserFactory
from apps.transactions.models import Transaction


class PlaywrightDashboardE2ETests(PlaywrightE2EBaseTestCase):
    def test_dashboard_filters_and_theme_toggle(self):
        user = UserFactory(
            username="e2e-dashboard-user",
            email="e2e-dashboard-user@example.com",
        )
        category = CategoryFactory(user=user, name="Casa", kind=Category.Kind.EXPENSE)
        TransactionFactory(
            user=user,
            category=category,
            kind=Transaction.Kind.EXPENSE,
            amount="200.00",
            transaction_date=date(2026, 3, 10),
            description="Conta antiga",
        )
        TransactionFactory(
            user=user,
            category=category,
            kind=Transaction.Kind.EXPENSE,
            amount="350.00",
            transaction_date=date(2026, 3, 26),
            description="Conta atual",
        )

        self.login(user.username)

        self.e2e("core-dashboard-date-from-input").fill("2026-03-20")
        self.e2e("core-dashboard-date-to-input").fill("2026-03-31")
        self.e2e("core-dashboard-filter-submit-click").click()

        expect(self.page).to_have_url(
            re.compile(r".*/dashboard/\?date_from=2026-03-20&date_to=2026-03-31$")
        )

        self.e2e("core-dashboard-clear-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/dashboard/?$"))

        was_dark = self.page.evaluate(
            "document.documentElement.classList.contains('dark')"
        )
        self.e2e("core-topbar-theme-toggle-click").click()
        is_dark = self.page.evaluate(
            "document.documentElement.classList.contains('dark')"
        )
        self.assertNotEqual(was_dark, is_dark)

    def test_dashboard_insights_flow_shows_summary_recent_and_placeholders(self):
        user = UserFactory(
            username="e2e-dashboard-insights-user",
            email="e2e-dashboard-insights-user@example.com",
        )
        income_category = CategoryFactory(
            user=user,
            name="Salario E2E Insights",
            kind=Category.Kind.INCOME,
        )
        expense_category = CategoryFactory(
            user=user,
            name="Moradia E2E Insights",
            kind=Category.Kind.EXPENSE,
        )

        income_description = "Salario mensal E2E Insights"
        expense_description = "Aluguel mensal E2E Insights"

        TransactionFactory(
            user=user,
            category=income_category,
            kind=Transaction.Kind.INCOME,
            amount="5000.00",
            transaction_date=date(2026, 3, 25),
            description=income_description,
            notes="Receita para validar dashboard",
        )
        TransactionFactory(
            user=user,
            category=expense_category,
            kind=Transaction.Kind.EXPENSE,
            amount="1800.00",
            transaction_date=date(2026, 3, 26),
            description=expense_description,
            notes="Despesa para validar dashboard",
        )

        self.login(user.username)

        expect(self.e2e("core-dashboard-filter-submit-click")).to_be_visible()

        expect(self.page.get_by_text("Saldo atual", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Receitas", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Despesas", exact=True)).to_be_visible()

        recent_transactions_section = self.page.locator("section").filter(
            has=self.page.get_by_text("Recentes", exact=True)
        )
        expect(recent_transactions_section.get_by_text(income_description, exact=True)).to_be_visible()
        expect(recent_transactions_section.get_by_text(expense_description, exact=True)).to_be_visible()

        expect(self.page.get_by_text("Maiores despesas", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Top 5", exact=True)).to_be_visible()

        expect(self.page.get_by_text("Importar CSV em breve", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Exportar Excel em breve", exact=True)).to_be_visible()
