import os
import re
from urllib.parse import parse_qs, urlparse

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright


class PlaywrightE2EBaseTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._original_async_unsafe = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        cls.playwright = sync_playwright().start()
        cls.playwright.selectors.set_test_id_attribute("data-e2e-selector")
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        if cls._original_async_unsafe is None:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE", None)
        else:
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = cls._original_async_unsafe
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.context = self.browser.new_context(base_url=self.live_server_url)
        self.page = self.context.new_page()

    def tearDown(self):
        self.context.close()
        super().tearDown()

    def e2e(self, selector: str):
        return self.page.get_by_test_id(selector)

    def login(self, username: str, password: str = "test-pass-123"):
        self.page.goto(f"{self.live_server_url}{reverse('accounts_http:login')}")
        self.e2e("accounts-login-username-input").fill(username)
        self.e2e("accounts-login-password-input").fill(password)
        self.e2e("accounts-login-submit-click").click()
        expect(self.page).to_have_url(re.compile(r".*/dashboard/?$"))

    def assert_redirects_to_login_with_next(self, protected_path: str):
        parsed_url = urlparse(self.page.url)
        self.assertIn("/contas/login/", parsed_url.path)

        query_params = parse_qs(parsed_url.query)
        self.assertIn("next", query_params)
        self.assertEqual(query_params["next"][0], protected_path)
