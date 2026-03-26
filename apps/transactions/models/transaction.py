from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.categories.models import Category
from config.models import BaseModel, Kind as TypeKind


class Transaction(BaseModel):
    Kind = TypeKind

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Usuário"),
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    category = models.ForeignKey(
        Category,
        verbose_name=_("Categoria"),
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    kind = models.CharField(_("Tipo"), max_length=20, choices=TypeKind.choices)
    amount = models.DecimalField(_("Valor"), max_digits=12, decimal_places=2)
    transaction_date = models.DateField(_("Data da Transação"))
    description = models.CharField(_("Descrição"), max_length=255, blank=True)
    notes = models.CharField(_("Observação"), max_length=500, blank=True)

    class Meta:
        """Model options intentionally explicit without schema-impacting settings."""

    def __str__(self) -> str:
        return f"{self.get_kind_display()} {self.amount}"
