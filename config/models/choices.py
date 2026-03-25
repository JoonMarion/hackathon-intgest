from django.db import models
from django.utils.translation import gettext_lazy as _


class Kind(models.TextChoices):
    INCOME = "income", _("Receita")
    EXPENSE = "expense", _("Despesa")
