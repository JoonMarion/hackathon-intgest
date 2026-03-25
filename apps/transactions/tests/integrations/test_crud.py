from datetime import date

from django.urls import reverse

from apps.categories.models import Category
from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import CategoryFactory, TransactionFactory, UserFactory
from apps.transactions.models import Transaction


class TransactionCRUDIntegrationTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username="transactions-crud-user", email="transactions-crud-user@example.com")
        self.other_user = UserFactory(
            username="transactions-crud-other-user",
            email="transactions-crud-other-user@example.com",
        )
        self.category = CategoryFactory(user=self.user, name="Alimentação", kind=Category.Kind.EXPENSE)
        self.income_category = CategoryFactory(user=self.user, name="Salário", kind=Category.Kind.INCOME)
        self.other_category = CategoryFactory(user=self.other_user, name="Outra", kind=Category.Kind.EXPENSE)

    def test_list_requires_authentication(self):
        url = reverse("transactions_http:index")
        login_url = reverse("accounts_http:login")

        response = self.client.get(url)

        self.assertRedirects(response, f"{login_url}?next={url}", fetch_redirect_response=False)

    def test_list_is_ordered_by_transaction_date_descending(self):
        self.client.force_login(self.user)
        older = TransactionFactory(
            user=self.user, category=self.category, kind=Transaction.Kind.EXPENSE,
            amount="20.00", transaction_date=date(2026, 3, 10), description="Mais antiga",
        )
        newer = TransactionFactory(
            user=self.user, category=self.category, kind=Transaction.Kind.EXPENSE,
            amount="30.00", transaction_date=date(2026, 3, 20), description="Mais recente",
        )

        response = self.client.get(reverse("transactions_http:index"))

        self.assertEqual(response.status_code, 200)
        transactions = list(response.context["transactions"])
        self.assertEqual(transactions, [newer, older])

    def test_create_creates_transaction_for_logged_in_user(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("transactions_http:create"),
            data={
                "category": self.category.pk,
                "kind": Transaction.Kind.EXPENSE,
                "amount": "75.50",
                "transaction_date": "2026-03-15",
                "description": "Almoço de negócios",
            },
        )

        self.assertRedirects(response, reverse("transactions_http:index"))
        created = Transaction.objects.get(description="Almoço de negócios")
        self.assertEqual(created.user, self.user)
        self.assertEqual(created.category, self.category)
        self.assertEqual(created.kind, Transaction.Kind.EXPENSE)
        self.assertEqual(str(created.amount), "75.50")
        self.assertEqual(created.transaction_date, date(2026, 3, 15))

    def test_update_changes_transaction_from_logged_in_user(self):
        own_transaction = TransactionFactory(
            user=self.user, category=self.category, kind=Transaction.Kind.EXPENSE,
            amount="50.00", transaction_date=date(2026, 3, 10), description="Original",
        )
        other_transaction = TransactionFactory(
            user=self.other_user, category=self.other_category, kind=Transaction.Kind.EXPENSE,
            amount="100.00", transaction_date=date(2026, 3, 10), description="Outra transação",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("transactions_http:update", args=[own_transaction.pk]),
            data={
                "category": self.category.pk,
                "kind": Transaction.Kind.EXPENSE,
                "amount": "80.00",
                "transaction_date": "2026-03-20",
                "description": "Atualizada",
            },
        )

        self.assertRedirects(response, reverse("transactions_http:index"))
        own_transaction.refresh_from_db()
        other_transaction.refresh_from_db()
        self.assertEqual(own_transaction.description, "Atualizada")
        self.assertEqual(str(own_transaction.amount), "80.00")
        self.assertEqual(other_transaction.description, "Outra transação")

    def test_delete_removes_transaction_from_logged_in_user(self):
        own_transaction = TransactionFactory(
            user=self.user, category=self.category, kind=Transaction.Kind.EXPENSE,
            amount="50.00", transaction_date=date(2026, 3, 10), description="Para deletar",
        )
        other_transaction = TransactionFactory(
            user=self.other_user, category=self.other_category, kind=Transaction.Kind.EXPENSE,
            amount="100.00", transaction_date=date(2026, 3, 10), description="Não deletar",
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse("transactions_http:delete", args=[own_transaction.pk]))

        self.assertRedirects(response, reverse("transactions_http:index"))
        self.assertFalse(Transaction.objects.filter(pk=own_transaction.pk).exists())
        self.assertTrue(Transaction.objects.filter(pk=other_transaction.pk).exists())

    def test_update_another_users_transaction_returns_404(self):
        other_transaction = TransactionFactory(
            user=self.other_user, category=self.other_category, kind=Transaction.Kind.EXPENSE,
            amount="100.00", transaction_date=date(2026, 3, 10), description="Protegida",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("transactions_http:update", args=[other_transaction.pk]),
            data={
                "category": self.category.pk,
                "kind": Transaction.Kind.EXPENSE,
                "amount": "999.00",
                "transaction_date": "2026-03-20",
                "description": "Não pode",
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_another_users_transaction_returns_404(self):
        other_transaction = TransactionFactory(
            user=self.other_user, category=self.other_category, kind=Transaction.Kind.EXPENSE,
            amount="100.00", transaction_date=date(2026, 3, 10), description="Protegida",
        )
        self.client.force_login(self.user)

        response = self.client.post(reverse("transactions_http:delete", args=[other_transaction.pk]))

        self.assertEqual(response.status_code, 404)

    def test_create_form_renders_for_authenticated_user(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("transactions_http:create"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)

    def test_create_with_invalid_data_renders_form_with_errors(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("transactions_http:create"),
            data={
                "category": self.category.pk,
                "kind": Transaction.Kind.EXPENSE,
                "amount": "0",
                "transaction_date": "2026-03-25",
                "description": "Inválida",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)

    def test_update_form_renders_with_existing_data(self):
        transaction = TransactionFactory(
            user=self.user, category=self.category, kind=Transaction.Kind.EXPENSE,
            amount="50.00", transaction_date=date(2026, 3, 10), description="Existente",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("transactions_http:update", args=[transaction.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].instance, transaction)

    def test_update_with_invalid_data_renders_form_with_errors(self):
        transaction = TransactionFactory(
            user=self.user, category=self.category, kind=Transaction.Kind.EXPENSE,
            amount="50.00", transaction_date=date(2026, 3, 10), description="Original",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("transactions_http:update", args=[transaction.pk]),
            data={
                "category": self.category.pk,
                "kind": Transaction.Kind.EXPENSE,
                "amount": "-5",
                "transaction_date": "2026-03-20",
                "description": "Inválida",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)


class TransactionFilterIntegrationTests(BaseIntegrationTestCase):
    def setUp(self):
        self.user = UserFactory(username="transactions-filter-user", email="transactions-filter-user@example.com")
        self.category_food = CategoryFactory(user=self.user, name="Alimentação", kind=Category.Kind.EXPENSE)
        self.category_salary = CategoryFactory(user=self.user, name="Salário", kind=Category.Kind.INCOME)
        self.expense = TransactionFactory(
            user=self.user, category=self.category_food, kind=Transaction.Kind.EXPENSE,
            amount="50.00", transaction_date=date(2026, 3, 20), description="Jantar restaurante",
        )
        self.income = TransactionFactory(
            user=self.user, category=self.category_salary, kind=Transaction.Kind.INCOME,
            amount="3000.00", transaction_date=date(2026, 3, 25), description="Salário mensal",
        )

    def test_filter_by_description_search(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("transactions_http:index"), {"q": "Jantar"})

        self.assertEqual(response.status_code, 200)
        transactions = list(response.context["transactions"])
        self.assertEqual(transactions, [self.expense])

    def test_filter_by_category(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("transactions_http:index"), {"category": self.category_food.pk})

        self.assertEqual(response.status_code, 200)
        transactions = list(response.context["transactions"])
        self.assertEqual(transactions, [self.expense])

    def test_filter_by_kind(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("transactions_http:index"), {"kind": "income"})

        self.assertEqual(response.status_code, 200)
        transactions = list(response.context["transactions"])
        self.assertEqual(transactions, [self.income])

    def test_filter_with_no_results(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("transactions_http:index"), {"q": "xyznotfound"})

        self.assertEqual(response.status_code, 200)
        transactions = list(response.context["transactions"])
        self.assertEqual(transactions, [])

    def test_categories_in_context_for_filter_dropdown(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("transactions_http:index"))

        self.assertEqual(response.status_code, 200)
        categories = list(response.context["categories"])
        self.assertEqual(categories, [self.category_food, self.category_salary])

    def test_filter_by_date_from(self):
        older = TransactionFactory(
            user=self.user, category=self.category_food, kind=Transaction.Kind.EXPENSE,
            amount="30.00", transaction_date=date(2026, 3, 10), description="Compra antiga",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("transactions_http:index"), {"date_from": "2026-03-20"})

        self.assertEqual(response.status_code, 200)
        transactions = list(response.context["transactions"])
        self.assertIn(self.income, transactions)
        self.assertIn(self.expense, transactions)
        self.assertNotIn(older, transactions)

    def test_filter_by_date_to(self):
        older = TransactionFactory(
            user=self.user, category=self.category_food, kind=Transaction.Kind.EXPENSE,
            amount="30.00", transaction_date=date(2026, 3, 10), description="Compra antiga",
        )
        self.client.force_login(self.user)

        response = self.client.get(reverse("transactions_http:index"), {"date_to": "2026-03-20"})

        self.assertEqual(response.status_code, 200)
        transactions = list(response.context["transactions"])
        self.assertIn(self.expense, transactions)
        self.assertIn(older, transactions)
        self.assertNotIn(self.income, transactions)

    def test_filter_by_date_range(self):
        older = TransactionFactory(
            user=self.user, category=self.category_food, kind=Transaction.Kind.EXPENSE,
            amount="30.00", transaction_date=date(2026, 3, 10), description="Compra antiga",
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("transactions_http:index"),
            {"date_from": "2026-03-15", "date_to": "2026-03-22"},
        )

        self.assertEqual(response.status_code, 200)
        transactions = list(response.context["transactions"])
        self.assertEqual(transactions, [self.expense])

    def test_combined_filters(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("transactions_http:index"),
            {"q": "Jantar", "kind": "expense"},
        )

        self.assertEqual(response.status_code, 200)
        transactions = list(response.context["transactions"])
        self.assertEqual(transactions, [self.expense])
