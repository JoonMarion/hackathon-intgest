from datetime import date

import factory
from django.contrib.auth import get_user_model

from apps.categories.models import Category
from apps.transactions.models import FinancialAccount, Transaction


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda index: f"user-{index}")
    email = factory.Sequence(lambda index: f"user-{index}@example.com")
    password = factory.PostGenerationMethodCall("set_password", "test-pass-123")


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    user = factory.SubFactory(UserFactory)
    name = factory.Faker("word")
    kind = Category.Kind.EXPENSE


class FinancialAccountFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FinancialAccount

    user = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda index: f"Conta {index}")


class TransactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Transaction

    user = factory.SubFactory(UserFactory)
    account = factory.SubFactory(FinancialAccountFactory, user=factory.SelfAttribute("..user"))
    category = factory.SubFactory(CategoryFactory, user=factory.SelfAttribute("..user"))
    kind = Transaction.Kind.EXPENSE
    amount = "10.00"
    transaction_date = date(2026, 3, 25)
    payee = factory.Faker("company")
    description = factory.Faker("sentence", nb_words=3)
