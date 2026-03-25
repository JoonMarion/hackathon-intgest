from io import StringIO
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db.models import F

from apps.categories.models import Category
from apps.core.tests.base import BaseIntegrationTestCase
from apps.transactions.models import Transaction


class SeedDemoDataCommandIntegrationTests(BaseIntegrationTestCase):
    def test_command_creates_predictable_counts_with_small_parameters(self):
        call_command(
            "seed_demo_data",
            users=2,
            categories_per_kind=1,
            transactions_per_user=2,
            seed=123,
        )

        UserModel = get_user_model()
        self.assertEqual(UserModel.objects.filter(username__startswith="demo").count(), 2)
        self.assertEqual(Category.objects.count(), 4)
        self.assertEqual(Transaction.objects.count(), 4)
        self.assertEqual(
            set(UserModel.objects.values_list("username", flat=True)),
            {"demo01", "demo02"},
        )

    def test_command_output_contains_generated_credentials(self):
        output = StringIO()

        call_command(
            "seed_demo_data",
            users=1,
            categories_per_kind=1,
            transactions_per_user=0,
            password="SenhaForte!2026",
            seed=7,
            stdout=output,
        )

        rendered_output = output.getvalue()
        self.assertIn("Credenciais de acesso:", rendered_output)
        self.assertIn("username: demo01", rendered_output)
        self.assertIn("email: demo01@example.com", rendered_output)
        self.assertIn("password: SenhaForte!2026", rendered_output)

    def test_reset_clears_demo_dataset_and_avoids_residual_duplication(self):
        UserModel = get_user_model()

        non_demo_user = UserModel.objects.create_user(
            username="demo_legacy_user",
            email="demo_legacy_user@corp.local",
            password="SenhaForte!2026",
        )
        non_demo_category = Category.objects.create(
            user=non_demo_user,
            name="Salário Legacy",
            kind=Category.Kind.INCOME,
        )
        Transaction.objects.create(
            user=non_demo_user,
            category=non_demo_category,
            kind=Category.Kind.INCOME,
            amount=Decimal("2500.00"),
            transaction_date=date(2026, 3, 25),
            description="Dados reais",
        )

        call_command(
            "seed_demo_data",
            users=2,
            categories_per_kind=1,
            transactions_per_user=1,
            seed=11,
        )
        call_command(
            "seed_demo_data",
            users=2,
            categories_per_kind=1,
            transactions_per_user=1,
            seed=11,
        )

        self.assertEqual(UserModel.objects.filter(email__iendswith="@example.com").count(), 4)
        self.assertEqual(Category.objects.count(), 9)
        self.assertEqual(Transaction.objects.count(), 5)

        call_command(
            "seed_demo_data",
            users=1,
            categories_per_kind=1,
            transactions_per_user=1,
            seed=11,
            reset=True,
        )

        self.assertEqual(UserModel.objects.filter(username__startswith="demo").count(), 2)
        self.assertEqual(UserModel.objects.filter(email__iendswith="@example.com").count(), 1)
        self.assertEqual(Category.objects.count(), 3)
        self.assertEqual(Transaction.objects.count(), 2)
        self.assertEqual(
            set(UserModel.objects.filter(email__iendswith="@example.com").values_list("username", flat=True)),
            {"demo01"},
        )
        self.assertTrue(UserModel.objects.filter(pk=non_demo_user.pk).exists())
        self.assertTrue(Category.objects.filter(pk=non_demo_category.pk).exists())
        self.assertEqual(Transaction.objects.filter(user=non_demo_user).count(), 1)

    def test_created_transactions_keep_kind_consistent_with_category_kind(self):
        call_command(
            "seed_demo_data",
            users=2,
            categories_per_kind=2,
            transactions_per_user=5,
            seed=2026,
        )

        self.assertGreater(Transaction.objects.count(), 0)
        mismatched = Transaction.objects.exclude(kind=F("category__kind")).count()
        self.assertEqual(mismatched, 0)
