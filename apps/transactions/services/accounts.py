from apps.transactions.models import FinancialAccount


def ensure_default_account(*, user) -> FinancialAccount:
    account, _ = FinancialAccount.objects.get_or_create(
        user=user,
        name="Conta principal",
        defaults={"is_active": True},
    )
    if not account.is_active:
        account.is_active = True
        account.save(update_fields=["is_active", "updated_at"])
    return account
