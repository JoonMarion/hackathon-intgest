from datetime import date
from decimal import Decimal
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.categories.models import Category
from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import CategoryFactory, TransactionFactory, UserFactory
from apps.transactions.models import DocumentFile, ExportJob, ImportJob, Transaction


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
            user=self.user,
            category=self.category,
            kind=Transaction.Kind.EXPENSE,
            amount="50.00",
            transaction_date=date(2026, 3, 10),
            description="Teste",
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

    def test_list_view_context_has_export_filter_payload(self):
        response = self.client.get(
            reverse("transactions_http:index"),
            {
                "q": "mercado",
                "category": "11",
                "kind": "expense",
                "date_from": "2026-03-01",
                "date_to": "2026-03-31",
                "ordering": "amount,created_at",
            },
        )

        payload = response.context["export_filter_payload"]
        self.assertEqual(payload["q"], "mercado")
        self.assertEqual(payload["category"], "11")
        self.assertEqual(payload["kind"], "expense")
        self.assertEqual(payload["date_from"], "2026-03-01")
        self.assertEqual(payload["date_to"], "2026-03-31")
        self.assertEqual(payload["ordering"], "amount,created_at")

    def test_list_view_context_has_categories(self):
        response = self.client.get(reverse("transactions_http:index"))

        self.assertIn("categories", response.context)

    def test_list_view_context_has_ordering_and_page_size_state(self):
        response = self.client.get(
            reverse("transactions_http:index"),
            {"ordering": "amount,created_at", "page_size": "10"},
        )

        self.assertEqual(response.context["current_ordering"], "amount,created_at")
        self.assertEqual(response.context["current_page_size"], 10)
        self.assertEqual(response.context["page_size_options"], (10, 25, 50))

    def test_list_view_context_falls_back_for_invalid_ordering_and_page_size(self):
        response = self.client.get(
            reverse("transactions_http:index"),
            {"ordering": "invalid", "page_size": "999"},
        )

        self.assertEqual(response.context["current_ordering"], "-transaction_date,-created_at")
        self.assertEqual(response.context["current_page_size"], 25)

    def test_list_view_context_has_filtered_summary(self):
        income_category = CategoryFactory(user=self.user, name="Salário", kind=Category.Kind.INCOME)
        TransactionFactory(
            user=self.user,
            category=income_category,
            kind=Transaction.Kind.INCOME,
            amount="3200.00",
            transaction_date=date(2026, 3, 25),
            description="Salário",
        )
        TransactionFactory(
            user=self.user,
            category=self.category,
            kind=Transaction.Kind.EXPENSE,
            amount="89.90",
            transaction_date=date(2026, 3, 20),
            description="Mercado",
        )

        response = self.client.get(reverse("transactions_http:index"), {"kind": "expense"})

        summary = response.context["filtered_summary"]
        self.assertEqual(summary["transaction_count"], 1)
        self.assertEqual(summary["income_count"], 0)
        self.assertEqual(summary["expense_count"], 1)
        self.assertEqual(summary["active_categories"], 1)
        self.assertEqual(summary["total_income"], Decimal("0.00"))
        self.assertEqual(summary["total_expense"], Decimal("89.90"))
        self.assertEqual(summary["net_total"], Decimal("-89.90"))
        self.assertTrue(response.context["has_active_filters"])

    def test_list_view_renders_import_export_actions(self):
        response = self.client.get(reverse("transactions_http:index"))

        self.assertContains(response, "Importar CSV/XLSX")
        self.assertContains(response, "Exportar CSV")
        self.assertContains(response, "Exportar XLSX")

    @patch("apps.transactions.http.views.db_transaction.on_commit")
    @patch("apps.transactions.http.views.execute_import_job")
    def test_import_confirm_queues_task_on_commit(self, execute_import_job_mock, on_commit_mock):
        source_file = DocumentFile.objects.create(
            user=self.user,
            purpose=DocumentFile.Purpose.IMPORT_SOURCE,
            original_name="lote.csv",
            content_type="text/csv",
            size_bytes=15,
            file=SimpleUploadedFile("lote.csv", b"Date,Amount\n2026-03-25,1.00\n", content_type="text/csv"),
        )
        import_job = ImportJob.objects.create(
            user=self.user,
            source_file=source_file,
            status=ImportJob.Status.DRAFT,
            column_mapping={"date": "Date", "amount": "Amount", "payee": "Payee", "account": "Account"},
        )

        response = self.client.post(reverse("transactions_http:import_confirm", args=[import_job.pk]))

        self.assertRedirects(response, reverse("transactions_http:import_status", args=[import_job.pk]))
        on_commit_mock.assert_called_once()
        execute_import_job_mock.enqueue.assert_not_called()

        callback = on_commit_mock.call_args.args[0]
        callback()
        execute_import_job_mock.enqueue.assert_called_once_with(import_job_id=import_job.pk)

    @patch("apps.transactions.http.views.db_transaction.on_commit")
    @patch("apps.transactions.http.views.generate_export_job")
    def test_export_create_queues_task_on_commit(self, generate_export_job_mock, on_commit_mock):
        response = self.client.post(
            reverse("transactions_http:export_create"),
            data={
                "format": "csv",
                "q": "",
                "category": "",
                "kind": "",
                "date_from": "",
                "date_to": "",
                "ordering": "-transaction_date,-created_at",
            },
        )

        export_job = ExportJob.objects.get(user=self.user)
        self.assertRedirects(response, reverse("transactions_http:export_status", args=[export_job.pk]))
        on_commit_mock.assert_called_once()
        generate_export_job_mock.enqueue.assert_not_called()

        callback = on_commit_mock.call_args.args[0]
        callback()
        generate_export_job_mock.enqueue.assert_called_once_with(export_job_id=export_job.pk)
