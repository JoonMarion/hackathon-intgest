from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from config.models import BaseModel


class ImportJob(BaseModel):
    class Status(models.TextChoices):
        DRAFT = "draft", _("Rascunho")
        QUEUED = "queued", _("Na fila")
        PROCESSING = "processing", _("Processando")
        COMPLETED = "completed", _("Concluído")
        FAILED = "failed", _("Falhou")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Usuário"),
        on_delete=models.CASCADE,
        related_name="import_jobs",
    )
    source_file = models.ForeignKey(
        "transactions.DocumentFile",
        verbose_name=_("Arquivo de origem"),
        on_delete=models.PROTECT,
        related_name="import_jobs",
    )
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices, default=Status.DRAFT)
    column_mapping = models.JSONField(_("Mapeamento de colunas"), default=dict, blank=True)
    preview_summary = models.JSONField(_("Resumo do preview"), default=dict, blank=True)
    preview_rows = models.JSONField(_("Linhas do preview"), default=list, blank=True)
    imported_rows = models.PositiveIntegerField(_("Linhas importadas"), default=0)
    skipped_rows = models.PositiveIntegerField(_("Linhas puladas"), default=0)
    failed_rows = models.PositiveIntegerField(_("Linhas com falha"), default=0)
    error_message = models.TextField(_("Erro"), blank=True)

    class Meta:
        """Model options intentionally explicit without schema-impacting settings."""


class ImportRowResult(BaseModel):
    class Status(models.TextChoices):
        IMPORTED = "imported", _("Importado")
        SKIPPED = "skipped", _("Pulado")
        FAILED = "failed", _("Falhou")

    import_job = models.ForeignKey(
        "transactions.ImportJob",
        verbose_name=_("Lote de importação"),
        on_delete=models.CASCADE,
        related_name="rows",
    )
    row_number = models.PositiveIntegerField(_("Número da linha"))
    status = models.CharField(_("Status"), max_length=20, choices=Status.choices)
    message = models.CharField(_("Mensagem"), max_length=255, blank=True)
    raw_data = models.JSONField(_("Dados brutos"), default=dict, blank=True)
    transaction = models.ForeignKey(
        "transactions.Transaction",
        verbose_name=_("Transação"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="import_rows",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["import_job", "row_number"],
                name="transactions_import_row_result_job_row_unique",
            )
        ]
