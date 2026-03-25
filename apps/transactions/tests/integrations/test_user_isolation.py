from datetime import date

from django.urls import reverse

from apps.categories.models import Category
from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import CategoryFactory, TransactionFactory, UserFactory
from apps.transactions.models import Transaction


class TransactionUserIsolationTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user_a = UserFactory(username="transactions-user-a", email="transactions-user-a@example.com")
        self.user_b = UserFactory(username="transactions-user-b", email="transactions-user-b@example.com")
        self.category_a = CategoryFactory(
            user=self.user_a,
            name="Categoria A",
            kind=Category.Kind.EXPENSE,
        )
        self.category_b = CategoryFactory(
            user=self.user_b,
            name="Categoria B",
            kind=Category.Kind.INCOME,
        )

        self.transaction_a = TransactionFactory(
            user=self.user_a,
            category=self.category_a,
            kind=Transaction.Kind.EXPENSE,
            amount="10.00",
            transaction_date=date(2026, 3, 25),
            description="Compra A",
        )
        self.transaction_b = TransactionFactory(
            user=self.user_b,
            category=self.category_b,
            kind=Transaction.Kind.INCOME,
            amount="20.00",
            transaction_date=date(2026, 3, 25),
            description="Receita B",
        )

    def test_user_only_sees_own_transactions(self):
        self.client.force_login(self.user_a)

        response = self.client.get(reverse("transactions_http:index"))

        self.assertEqual(response.status_code, 200)
        transactions = response.context["transactions"]
        self.assertQuerySetEqual(transactions, [self.transaction_a], transform=lambda item: item)
        self.assertNotIn(self.transaction_b, transactions)