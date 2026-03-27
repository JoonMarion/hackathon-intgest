import re

from django.urls import reverse
from playwright.sync_api import expect

from apps.core.tests.e2e.base import PlaywrightE2EBaseTestCase
from apps.core.tests.factories import UserFactory


class PlaywrightAccountsE2ETests(PlaywrightE2EBaseTestCase):
    def test_register_then_login_end_to_end(self):
        username = "e2e-register-user"
        email = "e2e-register-user@example.com"
        password = "Vz7!River-Cedar-2049"

        self.page.goto(f"{self.live_server_url}{reverse('accounts_http:login')}")
        self.e2e("accounts-login-register-link-click").click()

        expect(self.page).to_have_url(re.compile(r".*/contas/register/?$"))

        self.e2e("accounts-register-username-input").fill(username)
        self.e2e("accounts-register-email-input").fill(email)
        self.e2e("accounts-register-password1-input").fill(password)
        self.e2e("accounts-register-password2-input").fill(password)
        self.e2e("accounts-register-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/contas/login/?$"))
        expect(self.e2e("accounts-login-submit-click")).to_be_visible()

        self.e2e("accounts-login-username-input").fill(username)
        self.e2e("accounts-login-password-input").fill(password)
        self.e2e("accounts-login-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/dashboard/?$"))

    def test_profile_edit_end_to_end(self):
        user = UserFactory(
            username="e2e-profile-user",
            email="e2e-profile-user@example.com",
        )
        updated_username = "e2e-profile-user-updated"
        updated_email = "e2e-profile-user-updated@example.com"
        updated_first_name = "Maria"
        updated_last_name = "Silva"

        self.login(user.username)

        self.e2e("core-topbar-user-menu-toggle-click").click()
        self.e2e("core-topbar-profile-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/contas/perfil/?$"))

        self.e2e("accounts-profile-detail-edit-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/contas/perfil/editar/?$"))

        self.e2e("accounts-profile-edit-username-input").fill(updated_username)
        self.e2e("accounts-profile-edit-email-input").fill(updated_email)
        self.e2e("accounts-profile-edit-first-name-input").fill(updated_first_name)
        self.e2e("accounts-profile-edit-last-name-input").fill(updated_last_name)
        self.e2e("accounts-profile-edit-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/contas/perfil/?$"))
        expect(self.page.locator("#main-content").get_by_text(updated_email, exact=True)).to_be_visible()
        expect(self.page.get_by_text(updated_first_name, exact=True)).to_be_visible()
        expect(self.page.get_by_text(updated_last_name, exact=True)).to_be_visible()

        self.e2e("accounts-profile-detail-edit-link-click").click()
        expect(self.e2e("accounts-profile-edit-username-input")).to_have_value(updated_username)
        expect(self.e2e("accounts-profile-edit-email-input")).to_have_value(updated_email)
        expect(self.e2e("accounts-profile-edit-first-name-input")).to_have_value(updated_first_name)
        expect(self.e2e("accounts-profile-edit-last-name-input")).to_have_value(updated_last_name)

    def test_password_change_end_to_end(self):
        user = UserFactory(
            username="e2e-password-user",
            email="e2e-password-user@example.com",
        )
        new_password = "Wk9!Maple-Orbit-3051"

        self.login(user.username)

        self.e2e("core-topbar-user-menu-toggle-click").click()
        self.e2e("core-topbar-profile-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/contas/perfil/?$"))

        self.e2e("accounts-profile-detail-password-change-link-click").click()
        expect(self.page).to_have_url(re.compile(r".*/contas/perfil/senha/?$"))

        self.e2e("accounts-password-change-old-password-input").fill("test-pass-123")
        self.e2e("accounts-password-change-new-password1-input").fill(new_password)
        self.e2e("accounts-password-change-new-password2-input").fill(new_password)
        self.e2e("accounts-password-change-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/contas/perfil/?$"))
        expect(self.page.get_by_text("Senha alterada com sucesso.", exact=True)).to_be_visible()

        self.e2e("core-topbar-user-menu-toggle-click").click()
        self.e2e("core-topbar-logout-submit-click").click()
        expect(self.page).to_have_url(re.compile(r".*/contas/login/?$"))

        self.e2e("accounts-login-username-input").fill(user.username)
        self.e2e("accounts-login-password-input").fill(new_password)
        self.e2e("accounts-login-submit-click").click()

        expect(self.page).to_have_url(re.compile(r".*/dashboard/?$"))
