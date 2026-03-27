from django.conf import settings
from django.db import models
from django.db.models import Q
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
    account = models.ForeignKey(
        "transactions.FinancialAccount",
        verbose_name=_("Conta"),
        on_delete=models.PROTECT,
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
    payee = models.CharField(_("Favorecido"), max_length=255, blank=True)
    description = models.CharField(_("Descrição"), max_length=255, blank=True)
    notes = models.CharField(_("Observação"), max_length=500, blank=True)
    import_id = models.CharField(_("ID de importação"), max_length=120, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "import_id"],
                condition=~Q(import_id=""),
                name="transactions_transaction_user_import_id_unique",
            )
        ]
        indexes = [
            models.Index(
                fields=["user", "transaction_date", "amount", "payee"],
                name="transactions_tx_dedup_idx",
            )
        ]

    def __str__(self) -> str:
        label = self.payee.strip() if self.payee else self.get_kind_display()
        return f"{label} {self.amount}"
