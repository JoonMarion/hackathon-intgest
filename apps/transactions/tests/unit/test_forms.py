from apps.categories.models import Category
from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import CategoryFactory, UserFactory
from apps.transactions.http.forms import TransactionForm
from apps.transactions.models import Transaction


class TransactionFormTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username="transaction-form-user", email="transaction-form-user@example.com")
        self.other_user = UserFactory(
            username="transaction-form-other-user",
            email="transaction-form-other-user@example.com",
        )

    def test_amount_must_be_greater_than_zero(self):
        category = CategoryFactory(
            user=self.user,
            kind=Category.Kind.EXPENSE,
        )
        form = TransactionForm(
            user=self.user,
            data={
                "category": category.pk,
                "kind": Transaction.Kind.EXPENSE,
                "amount": "0.00",
                "transaction_date": "2026-03-25",
                "description": "Compra",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["amount"], ["Informe um valor maior que zero."])

    def test_category_from_another_user_is_invalid(self):
        other_user_category = CategoryFactory(
            user=self.other_user,
            kind=Category.Kind.EXPENSE,
        )

        form = TransactionForm(
            user=self.user,
            data={
                "category": other_user_category.pk,
                "kind": Transaction.Kind.EXPENSE,
                "amount": "10.00",
                "transaction_date": "2026-03-25",
                "description": "Compra",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("category", form.errors)

    def test_kind_must_match_category_kind(self):
        income_category = CategoryFactory(
            user=self.user,
            kind=Category.Kind.INCOME,
        )

        form = TransactionForm(
            user=self.user,
            data={
                "category": income_category.pk,
                "kind": Transaction.Kind.EXPENSE,
                "amount": "10.00",
                "transaction_date": "2026-03-25",
                "description": "Lançamento incompatível",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["kind"],
            ["O tipo da transação deve ser compatível com o tipo da categoria."],
        )
