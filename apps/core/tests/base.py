from django.test import SimpleTestCase, TestCase
from faker import Faker


class BaseUnitTestCase(SimpleTestCase):
    faker_seed = 20260325

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.faker = Faker()
        cls.faker.seed_instance(cls.faker_seed)


class BaseIntegrationTestCase(TestCase):
    faker_seed = 20260325

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.faker = Faker()
        cls.faker.seed_instance(cls.faker_seed)
