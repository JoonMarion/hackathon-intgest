import re

from django.urls import reverse
from playwright.sync_api import expect

from apps.core.tests.e2e.base import PlaywrightE2EBaseTestCase
from apps.core.tests.factories import UserFactory


class PlaywrightAuthNavigationE2ETests(PlaywrightE2EBaseTestCase):
    def test_protected_routes_redirect_to_login_when_unauthenticated(self):
        protected_paths = [
            reverse("core_http:index"),
            reverse("transactions_http:index"),
            reverse("categories_http:index"),
            reverse("accounts_http:profile"),
        ]

        for protected_path in protected_paths:
            self.page.goto(f"{self.live_server_url}{protected_path}")
            self.assert_redirects_to_login_with_next(protected_path)
            expect(self.e2e("accounts-login-submit-click")).to_be_visible()

    def test_cross_page_navigation_smoke_flow_authenticated(self):
        user = UserFactory(
            username="e2e-nav-user",
            email="e2e-nav-user@example.com",
        )

        self.login(user.username)

        self.e2e("core-sidebar-dashboard-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/dashboard/?$"))
        expect(self.e2e("core-dashboard-filter-submit-click")).to_be_visible()

        self.e2e("core-sidebar-transactions-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/lancamentos/?$"))
        expect(self.e2e("transactions-index-filter-submit-click")).to_be_visible()

        self.e2e("core-sidebar-categories-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/categorias/?$"))
        expect(self.e2e("categories-index-create-link-click")).to_be_visible()

        self.e2e("core-topbar-user-menu-toggle-click").click()
        expect(self.e2e("core-topbar-profile-link-click")).to_be_visible()
        self.e2e("core-topbar-profile-link-click").click()

        expect(self.page).to_have_url(re.compile(r".*/contas/perfil/?$"))
        expect(self.e2e("accounts-profile-detail-edit-link-click")).to_be_visible()

    def test_login_with_email_end_to_end(self):
        user = UserFactory(
            username="e2e-email-login-user",
            email="e2e-email-login-user@example.com",
        )

        self.page.goto(f"{self.live_server_url}{reverse('accounts_http:login')}")
        self.e2e("accounts-login-username-input").fill(user.email)
        self.e2e("accounts-login-password-input").fill("test-pass-123")
        self.e2e("accounts-login-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/dashboard/?$"))
        expect(self.e2e("core-dashboard-filter-submit-click")).to_be_visible()

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
