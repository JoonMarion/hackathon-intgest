from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.models import BaseModel


class FinancialAccount(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Usuário"),
        on_delete=models.CASCADE,
        related_name="financial_accounts",
    )
    name = models.CharField(_("Nome"), max_length=120)
    is_active = models.BooleanField(_("Ativa"), default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "name"],
                name="transactions_financial_account_user_name_unique",
            )
        ]

    def __str__(self) -> str:
        return self.name
