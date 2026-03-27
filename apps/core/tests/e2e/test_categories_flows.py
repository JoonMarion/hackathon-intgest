import re
from datetime import date

from playwright.sync_api import expect

from apps.categories.models import Category
from apps.core.tests.e2e.base import PlaywrightE2EBaseTestCase
from apps.core.tests.factories import CategoryFactory, UserFactory
from apps.transactions.models import Transaction


class PlaywrightCategoriesE2ETests(PlaywrightE2EBaseTestCase):
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

    def test_edit_category_end_to_end(self):
        user = UserFactory(
            username="e2e-category-edit-user",
            email="e2e-category-edit-user@example.com",
        )
        category = CategoryFactory(
            user=user,
            name="Original Category E2E",
            kind=Category.Kind.EXPENSE,
        )
        updated_name = "Updated Category E2E"

        self.login(user.username)

        self.e2e("core-sidebar-categories-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/categorias/?$"))

        self.e2e(f"categories-index-edit-link-click-{category.pk}").click()
        expect(self.page).to_have_url(re.compile(rf".*/categorias/{category.pk}/update/?$"))

        self.e2e("categories-form-name-input").fill(updated_name)
        self.e2e("categories-form-kind-select").select_option(Category.Kind.INCOME)
        self.e2e("categories-form-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/categorias/?$"))
        updated_category_link = self.e2e(f"categories-index-name-link-click-{category.pk}")
        expect(updated_category_link).to_be_visible()
        expect(updated_category_link).to_have_text(updated_name)

    def test_delete_category_end_to_end(self):
        user = UserFactory(
            username="e2e-category-delete-user",
            email="e2e-category-delete-user@example.com",
        )
        category = CategoryFactory(
            user=user,
            name="Delete Category E2E",
            kind=Category.Kind.EXPENSE,
        )

        self.login(user.username)

        self.e2e("core-sidebar-categories-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/categorias/?$"))

        self.e2e(f"categories-index-delete-link-click-{category.pk}").click()
        expect(self.page).to_have_url(re.compile(rf".*/categorias/{category.pk}/delete/?$"))

        self.e2e("categories-confirm-delete-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/categorias/?$"))
        expect(
            self.page.locator(f"[data-e2e-selector='categories-index-name-link-click-{category.pk}']")
        ).to_have_count(0)

    def test_cancel_delete_category_end_to_end(self):
        user = UserFactory(
            username="e2e-category-cancel-delete-user",
            email="e2e-category-cancel-delete-user@example.com",
        )
        category = CategoryFactory(
            user=user,
            name="Cancel Delete Category E2E",
            kind=Category.Kind.EXPENSE,
        )

        self.login(user.username)

        self.e2e("core-sidebar-categories-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/categorias/?$"))

        self.e2e(f"categories-index-delete-link-click-{category.pk}").click()
        expect(self.page).to_have_url(re.compile(rf".*/categorias/{category.pk}/delete/?$"))

        self.e2e("categories-confirm-delete-cancel-link-click").click()

        expect(self.page).to_have_url(re.compile(r".*/categorias/?$"))
        remaining_category_link = self.e2e(f"categories-index-name-link-click-{category.pk}")
        expect(remaining_category_link).to_be_visible()
        expect(remaining_category_link).to_have_text(category.name)
