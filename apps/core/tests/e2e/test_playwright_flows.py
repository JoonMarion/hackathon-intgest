import re
import os
from datetime import date

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from apps.categories.models import Category
from apps.core.tests.factories import CategoryFactory, TransactionFactory, UserFactory
from apps.transactions.models import Transaction


class PlaywrightSystemE2ETests(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._original_async_unsafe = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        cls.playwright = sync_playwright().start()
        cls.playwright.selectors.set_test_id_attribute("data-e2e-selector")
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        if cls._original_async_unsafe is None:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE", None)
        else:
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = cls._original_async_unsafe
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.context = self.browser.new_context(base_url=self.live_server_url)
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()
        super().tearDown()

    def e2e(self, selector: str):
        return self.page.get_by_test_id(selector)

    def login(self, username: str, password: str = "test-pass-123"):
        self.page.goto(f"{self.live_server_url}{reverse('accounts_http:login')}")
        self.e2e("accounts-login-username-input").fill(username)
        self.e2e("accounts-login-password-input").fill(password)
        self.e2e("accounts-login-submit-click").click()
        expect(self.page).to_have_url(re.compile(r".*/dashboard/?$"))

    def test_login_and_logout_by_topbar_menu(self):
        user = UserFactory(
            username="e2e-auth-user",
            email="e2e-auth-user@example.com",
        )

        self.login(user.username)

        self.e2e("core-topbar-user-menu-toggle-click").click()
        self.e2e("core-topbar-logout-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/contas/login/?$"))
        expect(self.e2e("accounts-login-submit-click")).to_be_visible()

    def test_create_category_and_transaction_end_to_end(self):
        user = UserFactory(
            username="e2e-crud-user",
            email="e2e-crud-user@example.com",
        )
        category_name = "E2E Moradia"
        transaction_description = "Aluguel E2E"

        self.login(user.username)

        self.e2e("core-sidebar-categories-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/categorias/?$"))
        self.e2e("categories-index-create-link-click").click()
        self.e2e("categories-form-name-input").fill(category_name)
        self.e2e("categories-form-kind-select").select_option(Category.Kind.EXPENSE)
        self.e2e("categories-form-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/categorias/?$"))
        created_category = self.page.locator(
            "[data-e2e-selector^='categories-index-name-link-click-']"
        ).filter(has_text=category_name).first
        expect(created_category).to_be_visible()

        self.e2e("core-sidebar-transactions-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/lancamentos/?$"))
        self.e2e("transactions-index-create-link-click").click()
        self.e2e("transactions-form-category-select").select_option(label=category_name)
        self.e2e("transactions-form-kind-select").select_option(Transaction.Kind.EXPENSE)
        self.e2e("transactions-form-amount-input").fill("1800.00")
        self.e2e("transactions-form-transaction-date-input").fill("2026-03-24")
        self.e2e("transactions-form-description-input").fill(transaction_description)
        self.e2e("transactions-form-notes-input").fill("Criado pelo fluxo e2e")
        self.e2e("transactions-form-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/lancamentos/?$"))
        expect(self.page.get_by_text(transaction_description)).to_be_visible()
        expect(
            self.page.locator("[data-e2e-selector^='transactions-index-edit-link-click-']")
        ).to_have_count(1)

    def test_transactions_filter_flow_uses_data_e2e_selectors(self):
        user = UserFactory(
            username="e2e-filter-user",
            email="e2e-filter-user@example.com",
        )
        expense_category = CategoryFactory(user=user, name="Mercado", kind=Category.Kind.EXPENSE)
        income_category = CategoryFactory(user=user, name="Salario", kind=Category.Kind.INCOME)
        TransactionFactory(
            user=user,
            category=expense_category,
            kind=Transaction.Kind.EXPENSE,
            amount="120.00",
            transaction_date=date(2026, 3, 21),
            description="Supermercado E2E",
        )
        TransactionFactory(
            user=user,
            category=income_category,
            kind=Transaction.Kind.INCOME,
            amount="5000.00",
            transaction_date=date(2026, 3, 21),
            description="Salario E2E",
        )

        self.login(user.username)

        self.e2e("core-sidebar-transactions-link-click").click()
        self.e2e("transactions-index-search-input").fill("Supermercado E2E")
        self.e2e("transactions-index-kind-select").select_option(Transaction.Kind.EXPENSE)
        self.e2e("transactions-index-filter-submit-click").click()

        expect(self.page.get_by_text("Supermercado E2E", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Salario E2E", exact=True)).to_have_count(0)

        self.e2e("transactions-index-clear-link-click").click()
        expect(self.e2e("transactions-index-search-input")).to_have_value("")
        expect(self.e2e("transactions-index-kind-select")).to_have_value("")

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