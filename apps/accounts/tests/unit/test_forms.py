from django.contrib.auth import get_user_model
from django.test import RequestFactory

from apps.accounts.http.forms import (
    EmailOrUsernameAuthenticationForm,
    RegisterForm,
    UserProfileForm,
)
from apps.core.tests.base import BaseIntegrationTestCase
from apps.core.tests.factories import UserFactory

User = get_user_model()


class RegisterFormTests(BaseIntegrationTestCase):
    def test_register_form_has_email_field(self):
        form = RegisterForm()
        self.assertIn("email", form.fields)
        self.assertTrue(form.fields["email"].required)

    def test_register_form_valid_data_creates_user_with_email(self):
        form = RegisterForm(
            data={
                "username": "register-user",
                "email": "register-user@example.com",
                "password1": "strong-pass-987!",
                "password2": "strong-pass-987!",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.email, "register-user@example.com")
        self.assertTrue(User.objects.filter(username="register-user").exists())

    def test_register_form_requires_email(self):
        form = RegisterForm(
            data={
                "username": "no-email-user",
                "email": "",
                "password1": "strong-pass-987!",
                "password2": "strong-pass-987!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_register_form_invalid_email_is_rejected(self):
        form = RegisterForm(
            data={
                "username": "bad-email-user",
                "email": "not-an-email",
                "password1": "strong-pass-987!",
                "password2": "strong-pass-987!",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_register_form_fields_order(self):
        self.assertEqual(
            RegisterForm.Meta.fields,
            ("username", "email", "password1", "password2"),
        )

    def test_register_form_duplicate_username_is_rejected_in_username_field(self):
        UserFactory(username="ExistingUser", email="existing-user@example.com")
        form = RegisterForm(
            data={
                "username": "existinguser",
                "email": "new-register@example.com",
                "password1": "strong-pass-987!",
                "password2": "strong-pass-987!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertEqual(
            form.errors["username"],
            [RegisterForm.duplicated_username_message],
        )

    def test_register_form_duplicate_email_is_rejected_in_email_field(self):
        UserFactory(username="existing-register", email="User@Example.com")
        form = RegisterForm(
            data={
                "username": "new-register",
                "email": "user@example.com",
                "password1": "strong-pass-987!",
                "password2": "strong-pass-987!",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertEqual(
            form.errors["email"],
            [RegisterForm.duplicated_email_message],
        )


class UserProfileFormTests(BaseIntegrationTestCase):
    def test_profile_form_blocks_duplicate_username_from_another_user(self):
        UserFactory(username="existing-user", email="existing@example.com")
        current_user = UserFactory(username="current-user", email="current@example.com")
        form = UserProfileForm(
            instance=current_user,
            data={
                "username": "Existing-User",
                "email": "current@example.com",
                "first_name": "Current",
                "last_name": "User",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)
        self.assertEqual(
            form.errors["username"],
            [UserProfileForm.duplicated_username_message],
        )

    def test_profile_form_blocks_duplicate_email_from_another_user(self):
        UserFactory(username="existing-user", email="existing@example.com")
        current_user = UserFactory(username="current-user", email="current@example.com")
        form = UserProfileForm(
            instance=current_user,
            data={
                "username": "current-user",
                "email": "EXISTING@EXAMPLE.COM",
                "first_name": "Current",
                "last_name": "User",
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertEqual(
            form.errors["email"],
            [UserProfileForm.duplicated_email_message],
        )

    def test_profile_form_allows_keeping_own_username_and_email(self):
        current_user = UserFactory(username="self-user", email="Self@Example.com")
        form = UserProfileForm(
            instance=current_user,
            data={
                "username": "self-user",
                "email": "self@example.com",
                "first_name": "Self",
                "last_name": "User",
            },
        )

        self.assertTrue(form.is_valid(), form.errors)


class EmailOrUsernameAuthenticationFormTests(BaseIntegrationTestCase):
    def setUp(self):
        super().setUp()
        self.request_factory = RequestFactory()
        self.request = self.request_factory.get("/accounts/login/")

    def test_login_form_label_is_usuario_ou_email(self):
        form = EmailOrUsernameAuthenticationForm(request=self.request)
        self.assertEqual(form.fields["username"].label, "Usuário ou e-mail")

    def test_login_with_username_authenticates(self):
        user = UserFactory(username="login-user")
        form = EmailOrUsernameAuthenticationForm(
            request=self.request,
            data={"username": "login-user", "password": "test-pass-123"},
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_login_with_email_authenticates(self):
        user = UserFactory(username="email-login", email="email-login@example.com")
        form = EmailOrUsernameAuthenticationForm(
            request=self.request,
            data={"username": "email-login@example.com", "password": "test-pass-123"},
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_login_with_email_case_insensitive(self):
        user = UserFactory(username="case-user", email="User@Example.com")
        form = EmailOrUsernameAuthenticationForm(
            request=self.request,
            data={"username": "user@example.com", "password": "test-pass-123"},
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_login_with_wrong_password_is_invalid(self):
        user = UserFactory(username="wrong-pass-user")
        form = EmailOrUsernameAuthenticationForm(
            request=self.request,
            data={"username": "wrong-pass-user", "password": "wrong-password"},
        )
        self.assertFalse(form.is_valid())

    def test_login_with_nonexistent_email_is_invalid(self):
        form = EmailOrUsernameAuthenticationForm(
            request=self.request,
            data={"username": "nobody@example.com", "password": "test-pass-123"},
        )
        self.assertFalse(form.is_valid())
