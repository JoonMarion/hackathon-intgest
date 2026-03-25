from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    class Kind(models.TextChoices):
        INCOME = "income", _("Receita")
        EXPENSE = "expense", _("Despesa")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Usuário"),
        on_delete=models.CASCADE,
        related_name="categories",
    )
    name = models.CharField(
        max_length=120,
        verbose_name=_("Nome"))
    
    kind = models.CharField(
        max_length=20,
        choices=Kind.choices,
        verbose_name=_("Tipo"))
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Criado em"))
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Atualizado em"))

    def __str__(self) -> str:
        return self.name
