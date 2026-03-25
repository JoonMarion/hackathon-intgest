from __future__ import annotations

import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import QuerySet

from faker import Faker

from apps.categories.models import Category
from apps.transactions.models import Transaction
from config.models import Kind


class Command(BaseCommand):
    help = "Popula dados de demonstração (usuários, categorias e transações)."

    DEMO_PREFIX = "demo"
    DEFAULT_DEMO_EMAIL_DOMAIN = "example.com"

    def add_arguments(self, parser) -> None:
        parser.add_argument("--users", type=int, default=3)
        parser.add_argument("--categories-per-kind", type=int, default=5)
        parser.add_argument("--transactions-per-user", type=int, default=30)
        parser.add_argument("--password", type=str, default="demo12345!")
        parser.add_argument("--demo-email-domain", type=str, default=self.DEFAULT_DEMO_EMAIL_DOMAIN)
        parser.add_argument("--seed", type=int, default=None)
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **options) -> None:
        users_count = options["users"]
        categories_per_kind = options["categories_per_kind"]
        transactions_per_user = options["transactions_per_user"]
        password = options["password"]
        demo_email_domain = options["demo_email_domain"].lower().strip().lstrip("@")
        seed = options["seed"]
        should_reset = options["reset"]

        self._validate_inputs(
            users_count=users_count,
            categories_per_kind=categories_per_kind,
            transactions_per_user=transactions_per_user,
            demo_email_domain=demo_email_domain,
        )

        faker = Faker("pt_BR")
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

        created_users: list = []
        UserModel = get_user_model()

        with transaction.atomic():
            demo_users = self._get_demo_users(email_domain=demo_email_domain)

            if should_reset:
                self._reset_demo_data(demo_users=demo_users)
                demo_users = self._get_demo_users(email_domain=demo_email_domain)

            existing_demo_users = demo_users.count()

            for index in range(users_count):
                sequence = existing_demo_users + index + 1
                username = f"{self.DEMO_PREFIX}{sequence:02d}"
                email = f"{username}@{demo_email_domain}"

                user = UserModel.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )

                user_categories = self._create_categories_for_user(
                    user=user,
                    faker=faker,
                    categories_per_kind=categories_per_kind,
                )
                self._create_transactions_for_user(
                    user=user,
                    faker=faker,
                    user_categories=user_categories,
                    transactions_per_user=transactions_per_user,
                )
                created_users.append(user)

        self._print_summary(
            users_count=len(created_users),
            categories_count=len(created_users) * categories_per_kind * 2,
            transactions_count=len(created_users) * transactions_per_user,
        )
        self._print_credentials(users=created_users, password=password)

    def _validate_inputs(
        self,
        *,
        users_count: int,
        categories_per_kind: int,
        transactions_per_user: int,
        demo_email_domain: str,
    ) -> None:
        if users_count < 1:
            raise CommandError("--users deve ser maior ou igual a 1.")
        if categories_per_kind < 1:
            raise CommandError("--categories-per-kind deve ser maior ou igual a 1.")
        if transactions_per_user < 0:
            raise CommandError("--transactions-per-user deve ser maior ou igual a 0.")
        if not demo_email_domain:
            raise CommandError("--demo-email-domain deve ser informado.")

    def _get_demo_users(self, *, email_domain: str) -> QuerySet:
        UserModel = get_user_model()
        return UserModel.objects.filter(
            username__startswith=self.DEMO_PREFIX,
            email__iendswith=f"@{email_domain}",
        )

    def _reset_demo_data(self, *, demo_users: QuerySet) -> None:

        Transaction.objects.filter(user__in=demo_users).delete()
        Category.objects.filter(user__in=demo_users).delete()
        demo_users.delete()

    def _create_categories_for_user(
        self,
        *,
        user,
        faker: Faker,
        categories_per_kind: int,
    ) -> dict[str, list[Category]]:
        categories_by_kind: dict[str, list[Category]] = {
            Kind.INCOME: [],
            Kind.EXPENSE: [],
        }

        for kind in (Kind.INCOME, Kind.EXPENSE):
            for _ in range(categories_per_kind):
                name = f"{faker.word().capitalize()} {faker.random_int(min=100, max=999)}"
                category = Category.objects.create(
                    user=user,
                    name=f"{name} {kind}",
                    kind=kind,
                )
                categories_by_kind[kind].append(category)

        return categories_by_kind

    def _create_transactions_for_user(
        self,
        *,
        user,
        faker: Faker,
        user_categories: dict[str, list[Category]],
        transactions_per_user: int,
    ) -> None:
        for _ in range(transactions_per_user):
            kind = random.choice([Kind.INCOME, Kind.EXPENSE])
            category = random.choice(user_categories[kind])
            amount = Decimal(f"{faker.pydecimal(left_digits=3, right_digits=2, positive=True)}").quantize(
                Decimal("0.01"),
            )

            Transaction.objects.create(
                user=user,
                category=category,
                kind=kind,
                amount=amount,
                transaction_date=faker.date_between(start_date="-365d", end_date="today"),
                description=faker.sentence(nb_words=4),
            )

    def _print_summary(
        self,
        *,
        users_count: int,
        categories_count: int,
        transactions_count: int,
    ) -> None:
        self.stdout.write(self.style.SUCCESS("Dados de demonstração gerados com sucesso."))
        self.stdout.write(f"- Usuários criados: {users_count}")
        self.stdout.write(f"- Categorias criadas: {categories_count}")
        self.stdout.write(f"- Transações criadas: {transactions_count}")

    def _print_credentials(self, *, users: list, password: str) -> None:
        self.stdout.write("\nCredenciais de acesso:")
        for user in users:
            self.stdout.write(
                f"- username: {user.username} | email: {user.email} | password: {password}",
            )