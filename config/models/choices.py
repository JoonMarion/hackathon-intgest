from django.db import models
from django.utils.translation import gettext_lazy as _


class CategoryKind(models.TextChoices):
    INCOME = "income", _("Receita")
    EXPENSE = "expense", _("Despesa")


class TransactionKind(models.TextChoices):
    INCOME = "income", _("Receita")
    EXPENSE = "expense", _("Despesa")
