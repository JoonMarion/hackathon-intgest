import json
from datetime import date
from decimal import Decimal

from django.urls import reverse

from apps.categories.models import Category
from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import (
    CategoryFactory,
    TransactionFactory,
    UserFactory,
)
from apps.transactions.models import Transaction


class DashboardViewIntegrationTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(
            username="dashboard-user", email="dashboard-user@example.com"
        )
        self.other_user = UserFactory(
            username="dashboard-other-user",
            email="dashboard-other-user@example.com",
        )
        self.url = reverse("core_http:index")

    def test_dashboard_requires_authentication(self):
        response = self.client.get(self.url)
        login_url = reverse("accounts_http:login")
        self.assertRedirects(response, f"{login_url}?next={self.url}")

    def test_dashboard_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/pages/index.html")

    def test_summary_totals_with_no_transactions(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context["total_income"], Decimal("0"))
        self.assertEqual(response.context["total_expense"], Decimal("0"))
        self.assertEqual(response.context["balance"], Decimal("0"))

    def test_summary_totals_computed_correctly(self):
        income_cat = CategoryFactory(
            user=self.user, kind=Category.Kind.INCOME, name="Salary"
        )
        expense_cat = CategoryFactory(
            user=self.user, kind=Category.Kind.EXPENSE, name="Food"
        )
        TransactionFactory(
            user=self.user,
            category=income_cat,
            kind=Transaction.Kind.INCOME,
            amount="100.00",
            transaction_date=date(2026, 3, 15),
        )
        TransactionFactory(
            user=self.user,
            category=income_cat,
            kind=Transaction.Kind.INCOME,
            amount="200.00",
            transaction_date=date(2026, 3, 16),
        )
        TransactionFactory(
            user=self.user,
            category=expense_cat,
            kind=Transaction.Kind.EXPENSE,
            amount="50.00",
            transaction_date=date(2026, 3, 17),
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context["total_income"], Decimal("300"))
        self.assertEqual(response.context["total_expense"], Decimal("50"))
        self.assertEqual(response.context["balance"], Decimal("250"))

    def test_summary_totals_only_include_own_transactions(self):
        other_cat = CategoryFactory(
            user=self.other_user, kind=Category.Kind.INCOME, name="Other Income"
        )
        TransactionFactory(
            user=self.other_user,
            category=other_cat,
            kind=Transaction.Kind.INCOME,
            amount="500.00",
            transaction_date=date(2026, 3, 10),
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.context["total_income"], Decimal("0"))
        self.assertEqual(response.context["total_expense"], Decimal("0"))
        self.assertEqual(response.context["balance"], Decimal("0"))

    def test_recent_transactions_shows_latest_five(self):
        cat = CategoryFactory(user=self.user, kind=Category.Kind.EXPENSE, name="Misc")
        for i in range(7):
            TransactionFactory(
                user=self.user,
                category=cat,
                kind=Transaction.Kind.EXPENSE,
                amount="10.00",
                transaction_date=date(2026, 3, 1 + i),
            )

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        recent = response.context["recent_transactions"]
        self.assertEqual(len(recent), 5)
        dates = [t.transaction_date for t in recent]
        self.assertEqual(dates, sorted(dates, reverse=True))

    def test_recent_transactions_only_include_own(self):
        user_cat = CategoryFactory(
            user=self.user, kind=Category.Kind.EXPENSE, name="UserCat"
        )
        other_cat = CategoryFactory(
            user=self.other_user, kind=Category.Kind.EXPENSE, name="OtherCat"
        )
        TransactionFactory(
            user=self.user,
            category=user_cat,
            kind=Transaction.Kind.EXPENSE,
            amount="10.00",
            transaction_date=date(2026, 3, 20),
        )
        TransactionFactory(
            user=self.other_user,
            category=other_cat,
            kind=Transaction.Kind.EXPENSE,
            amount="99.00",
            transaction_date=date(2026, 3, 20),
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        recent = response.context["recent_transactions"]
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].user, self.user)

    def test_chart_labels_present_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        ctx = response.context
        for key in ("chart_labels", "chart_income", "chart_expense"):
            self.assertIn(key, ctx)
            parsed = json.loads(ctx[key])
            self.assertIsInstance(parsed, list)

    def test_category_breakdown_data_in_context(self):
        income_cat = CategoryFactory(
            user=self.user, kind=Category.Kind.INCOME, name="Freelance"
        )
        expense_cat1 = CategoryFactory(
            user=self.user, kind=Category.Kind.EXPENSE, name="Food"
        )
        expense_cat2 = CategoryFactory(
            user=self.user, kind=Category.Kind.EXPENSE, name="Transport"
        )
        TransactionFactory(
            user=self.user,
            category=income_cat,
            kind=Transaction.Kind.INCOME,
            amount="500.00",
            transaction_date=date(2026, 3, 10),
        )
        TransactionFactory(
            user=self.user,
            category=expense_cat1,
            kind=Transaction.Kind.EXPENSE,
            amount="80.00",
            transaction_date=date(2026, 3, 11),
        )
        TransactionFactory(
            user=self.user,
            category=expense_cat2,
            kind=Transaction.Kind.EXPENSE,
            amount="40.00",
            transaction_date=date(2026, 3, 12),
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        ctx = response.context

        expense_labels = json.loads(ctx["expense_categories_labels"])
        expense_data = json.loads(ctx["expense_categories_data"])
        self.assertIn("Food", expense_labels)
        self.assertIn("Transport", expense_labels)
        food_idx = expense_labels.index("Food")
        transport_idx = expense_labels.index("Transport")
        self.assertEqual(expense_data[food_idx], 80.0)
        self.assertEqual(expense_data[transport_idx], 40.0)

        income_labels = json.loads(ctx["income_categories_labels"])
        income_data = json.loads(ctx["income_categories_data"])
        self.assertIn("Freelance", income_labels)
        freelance_idx = income_labels.index("Freelance")
        self.assertEqual(income_data[freelance_idx], 500.0)

    def test_category_breakdown_only_includes_own(self):
        other_cat = CategoryFactory(
            user=self.other_user, kind=Category.Kind.EXPENSE, name="OtherExpense"
        )
        TransactionFactory(
            user=self.other_user,
            category=other_cat,
            kind=Transaction.Kind.EXPENSE,
            amount="999.00",
            transaction_date=date(2026, 3, 5),
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)
        ctx = response.context

        expense_labels = json.loads(ctx["expense_categories_labels"])
        expense_data = json.loads(ctx["expense_categories_data"])
        self.assertNotIn("OtherExpense", expense_labels)
        self.assertEqual(expense_data, [])

    def test_dashboard_with_date_range_filter(self):
        """Date range filter narrows summary totals."""
        cat = CategoryFactory(
            user=self.user, kind=Category.Kind.INCOME, name="Inc"
        )
        TransactionFactory(
            user=self.user,
            category=cat,
            kind=Transaction.Kind.INCOME,
            amount="100.00",
            transaction_date=date(2026, 1, 15),
        )
        TransactionFactory(
            user=self.user,
            category=cat,
            kind=Transaction.Kind.INCOME,
            amount="200.00",
            transaction_date=date(2026, 3, 15),
        )

        self.client.force_login(self.user)
        response = self.client.get(
            self.url, {"date_from": "2026-03-01", "date_to": "2026-03-31"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_income"], Decimal("200"))

    def test_dashboard_filter_preserves_current_filters_in_context(self):
        """Submitted filter values appear in current_filters context."""
        self.client.force_login(self.user)
        response = self.client.get(
            self.url, {"date_from": "2026-01-01", "date_to": "2026-06-30"}
        )
        filters = response.context["current_filters"]
        self.assertEqual(filters["date_from"], "2026-01-01")
        self.assertEqual(filters["date_to"], "2026-06-30")

    def test_dashboard_no_filter_has_empty_current_filters(self):
        """Without filter params, current_filters has empty strings."""
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        filters = response.context["current_filters"]
        self.assertEqual(filters["date_from"], "")
        self.assertEqual(filters["date_to"], "")

    def test_dashboard_invalid_date_ignored(self):
        """Invalid date params are treated as no filter."""
        self.client.force_login(self.user)
        response = self.client.get(self.url, {"date_from": "not-a-date"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["current_filters"]["date_from"], "")
