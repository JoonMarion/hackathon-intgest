from datetime import date

from django.urls import reverse

from apps.categories.models import Category
from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import CategoryFactory, TransactionFactory, UserFactory
from apps.transactions.models import Transaction


class TransactionViewConfigTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username="view-config-user", email="view-config-user@example.com")
        self.category = CategoryFactory(user=self.user, name="Alimentação", kind=Category.Kind.EXPENSE)
        self.client.force_login(self.user)

    def test_list_view_uses_correct_template(self):
        response = self.client.get(reverse("transactions_http:index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "transactions/pages/index.html")

    def test_create_view_uses_correct_template(self):
        response = self.client.get(reverse("transactions_http:create"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "transactions/pages/form.html")

    def test_update_view_uses_correct_template(self):
        transaction = TransactionFactory(
            user=self.user, category=self.category, kind=Transaction.Kind.EXPENSE,
            amount="50.00", transaction_date=date(2026, 3, 10), description="Teste",
        )

        response = self.client.get(reverse("transactions_http:update", args=[transaction.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "transactions/pages/form.html")

    def test_create_view_passes_user_to_form(self):
        response = self.client.get(reverse("transactions_http:create"))

        self.assertEqual(response.context["form"].user, self.user)

    def test_list_view_context_has_current_filters(self):
        response = self.client.get(reverse("transactions_http:index"))

        self.assertIn("current_filters", response.context)
        current_filters = response.context["current_filters"]
        for key in ("q", "category", "kind", "date_from", "date_to"):
            self.assertIn(key, current_filters)

    def test_list_view_context_has_categories(self):
        response = self.client.get(reverse("transactions_http:index"))

        self.assertIn("categories", response.context)
