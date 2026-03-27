import re
from datetime import date

from playwright.sync_api import expect

from apps.categories.models import Category
from apps.core.tests.e2e.base import PlaywrightE2EBaseTestCase
from apps.core.tests.factories import CategoryFactory, TransactionFactory, UserFactory
from apps.transactions.models import Transaction


class PlaywrightTransactionsE2ETests(PlaywrightE2EBaseTestCase):
    def test_edit_transaction_end_to_end(self):
        user = UserFactory(
            username="e2e-transaction-edit-user",
            email="e2e-transaction-edit-user@example.com",
        )
        category = CategoryFactory(
            user=user,
            name="Casa E2E",
            kind=Category.Kind.EXPENSE,
        )
        transaction = TransactionFactory(
            user=user,
            category=category,
            kind=Transaction.Kind.EXPENSE,
            amount="120.00",
            transaction_date=date(2026, 3, 24),
            description="Conta antiga E2E",
            notes="Observacao antiga",
        )

        updated_description = "Conta atualizada E2E"

        self.login(user.username)

        self.e2e("core-sidebar-transactions-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/lancamentos/?$"))

        self.e2e(f"transactions-index-edit-link-click-{transaction.pk}").click()
        expect(self.page).to_have_url(re.compile(rf".*/lancamentos/{transaction.pk}/update/?$"))

        self.e2e("transactions-form-category-select").select_option(str(category.pk))
        self.e2e("transactions-form-kind-select").select_option(Transaction.Kind.EXPENSE)
        self.e2e("transactions-form-amount-input").fill("260.75")
        self.e2e("transactions-form-transaction-date-input").fill("2026-03-27")
        self.e2e("transactions-form-description-input").fill(updated_description)
        self.e2e("transactions-form-notes-input").fill("Atualizado pelo fluxo e2e")
        self.e2e("transactions-form-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/lancamentos/?$"))
        expect(self.page.get_by_text(updated_description, exact=True)).to_be_visible()

        transaction.refresh_from_db()
        self.assertEqual(transaction.description, updated_description)

    def test_delete_transaction_end_to_end(self):
        user = UserFactory(
            username="e2e-transaction-delete-user",
            email="e2e-transaction-delete-user@example.com",
        )
        category = CategoryFactory(
            user=user,
            name="Delete Transaction Category E2E",
            kind=Category.Kind.EXPENSE,
        )
        transaction = TransactionFactory(
            user=user,
            category=category,
            kind=Transaction.Kind.EXPENSE,
            description="Delete Transaction E2E",
        )

        self.login(user.username)

        self.e2e("core-sidebar-transactions-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/lancamentos/?$"))

        self.e2e(f"transactions-index-delete-link-click-{transaction.pk}").click()
        expect(self.page).to_have_url(re.compile(rf".*/lancamentos/{transaction.pk}/delete/?$"))

        self.e2e("transactions-confirm-delete-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/lancamentos/?$"))
        expect(self.page.get_by_text("Delete Transaction E2E", exact=True)).to_have_count(0)
        self.assertFalse(Transaction.objects.filter(pk=transaction.pk).exists())

    def test_cancel_delete_transaction_end_to_end(self):
        user = UserFactory(
            username="e2e-transaction-cancel-delete-user",
            email="e2e-transaction-cancel-delete-user@example.com",
        )
        category = CategoryFactory(
            user=user,
            name="Cancel Delete Transaction Category E2E",
            kind=Category.Kind.EXPENSE,
        )
        transaction = TransactionFactory(
            user=user,
            category=category,
            kind=Transaction.Kind.EXPENSE,
            description="Cancel Delete Transaction E2E",
        )

        self.login(user.username)

        self.e2e("core-sidebar-transactions-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/lancamentos/?$"))

        self.e2e(f"transactions-index-delete-link-click-{transaction.pk}").click()
        expect(self.page).to_have_url(re.compile(rf".*/lancamentos/{transaction.pk}/delete/?$"))

        self.e2e("transactions-confirm-delete-cancel-link-click").click()

        expect(self.page).to_have_url(re.compile(r".*/lancamentos/?$"))
        remaining_transaction = self.page.get_by_text("Cancel Delete Transaction E2E", exact=True)
        expect(remaining_transaction).to_be_visible()
        self.assertTrue(Transaction.objects.filter(pk=transaction.pk).exists())

    def test_transactions_pagination_and_ordering_flow_uses_data_e2e_selectors(self):
        user = UserFactory(
            username="e2e-pagination-user",
            email="e2e-pagination-user@example.com",
        )
        category = CategoryFactory(
            user=user,
            name="Pagination Category E2E",
            kind=Category.Kind.EXPENSE,
        )

        for day in range(1, 13):
            TransactionFactory(
                user=user,
                category=category,
                kind=Transaction.Kind.EXPENSE,
                amount=f"{100 + day}.00",
                transaction_date=date(2026, 3, day),
                description=f"Pagination Transaction E2E {day:02d}",
                notes=f"Pagination notes {day:02d}",
            )

        self.login(user.username)

        self.e2e("core-sidebar-transactions-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/lancamentos/?$"))

        self.e2e("transactions-index-page-size-select").select_option("10")
        self.e2e("transactions-index-ordering-select").select_option("transaction_date,created_at")
        self.e2e("transactions-index-filter-submit-click").click()

        expect(self.e2e("transactions-index-page-size-select")).to_have_value("10")
        expect(self.e2e("transactions-index-ordering-select")).to_have_value("transaction_date,created_at")
        expect(self.page.get_by_text("Pagination Transaction E2E 01", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Pagination Transaction E2E 10", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Pagination Transaction E2E 11", exact=True)).to_have_count(0)

        self.e2e("transactions-index-pagination-next-link-click").click()

        expect(self.page).to_have_url(re.compile(r".*/lancamentos/\?.*page=2.*$"))
        expect(self.e2e("transactions-index-page-size-select")).to_have_value("10")
        expect(self.e2e("transactions-index-ordering-select")).to_have_value("transaction_date,created_at")
        expect(self.page.get_by_text("Pagination Transaction E2E 11", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Pagination Transaction E2E 12", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Pagination Transaction E2E 01", exact=True)).to_have_count(0)

        self.e2e("transactions-index-pagination-previous-link-click").click()

        expect(self.page).to_have_url(re.compile(r".*/lancamentos/\?.*page=1.*$"))
        expect(self.page.get_by_text("Pagination Transaction E2E 01", exact=True)).to_be_visible()

        self.e2e("transactions-index-ordering-select").select_option("-transaction_date,-created_at")
        self.e2e("transactions-index-filter-submit-click").click()

        expect(self.e2e("transactions-index-ordering-select")).to_have_value("-transaction_date,-created_at")
        expect(self.page.get_by_text("Pagination Transaction E2E 12", exact=True)).to_be_visible()
        expect(self.page.get_by_text("Pagination Transaction E2E 01", exact=True)).to_have_count(0)

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
