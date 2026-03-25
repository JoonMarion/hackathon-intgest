> ⚠️ Legacy reference: inherited from another project. Tenant/PostgreSQL-specific migration patterns are not primary guidance here.
> Use `docs/README.md`, `RULES.md`, and `PRODUCT.md` first.

# Migration Guide

Reference patterns for Django schema and data migrations in IntGestPED. For behavioral rules and safety constraints, see the [Migration Writer agent](../.github/agents/migration-writer.agent.md).

## Migration Types

| Type | When | Command |
|------|------|---------|
| Schema migration | Adding/removing models or fields | `python manage.py makemigrations <app_name>` |
| Data migration (empty) | Backfilling or transforming data | `python manage.py makemigrations <app_name> --empty -n <name>` |

After generating a schema migration, verify:
- Correct `dependencies`
- No unexpected changes
- Proper `Meta` options preserved

## Multi-Tenant Data Migration Pattern

IntGestPED uses `django-tenants`. Data migrations must iterate over all tenant schemas using `schema_context`:

```python
from django.db import migrations

def forward_migration(apps, schema_editor):
    from django_tenants.utils import schema_context, get_tenant_model

    TenantModel = get_tenant_model()

    for tenant in TenantModel.objects.exclude(schema_name='public'):
        with schema_context(tenant.schema_name):
            MyModel = apps.get_model('app_name', 'MyModel')
            _backfill_tenant_data(MyModel)

def _backfill_tenant_data(MyModel):
    """Process data for a single tenant."""
    queryset = MyModel.objects.all().iterator(chunk_size=500)
    batch = []
    for obj in queryset:
        batch.append(obj)
        if len(batch) >= 500:
            MyModel.objects.bulk_create(batch, ignore_conflicts=True)
            batch = []
    if batch:
        MyModel.objects.bulk_create(batch, ignore_conflicts=True)

class Migration(migrations.Migration):
    dependencies = [
        ('app_name', 'previous_migration'),
    ]
    operations = [
        migrations.RunPython(forward_migration, migrations.RunPython.noop, atomic=True),
    ]
```

> Always call `apps.get_model()` **inside** the migration function — the historical model registry is only available during the migration run.

## Wave Ordering

When a feature requires multiple migrations, sequence them in waves. Each wave declares explicit `dependencies` on the previous:

| Wave | Type | Example name |
|------|------|--------------|
| A | Schema (CreateModel, AddField) — always first | `0042_create_payment_note_file_table` |
| B | Core data backfill | `0043_backfill_original_files` |
| C | Type-specific backfill | `0044_backfill_payment_notes_from_file` |
| D | Relationship migrations (FK/M2M) | `0045_populate_payment_note_commitments_m2m` |

## Performance Rules

- Use `iterator(chunk_size=500)` — prevents loading all rows into memory at once
- Use `bulk_create()` / `bulk_update()` instead of per-object `.save()` calls
- Batch in groups of 500–1 000 rows
- Use `ignore_conflicts=True` where idempotency is required

## Idempotency

Data migrations must be safe to run more than once:

```python
# ✅ Idempotent — bulk_create with ignore_conflicts
NewModel.objects.bulk_create(objects, ignore_conflicts=True)

# ✅ Idempotent — guard with .exists()
if not NewModel.objects.filter(original_id=old_obj.pk).exists():
    NewModel.objects.create(...)

# ❌ Not idempotent — creates duplicates on re-run
NewModel.objects.create(data=old_obj.data)
```

## Post-Migration Verification

```bash
# Apply to all tenant schemas (never use plain migrate)
python manage.py migrate_schemas

# Confirm no pending migrations remain
python manage.py makemigrations --check

# Spot-check row counts in a sample tenant
python manage.py shell -c "
from django_tenants.utils import schema_context, get_tenant_model
for t in get_tenant_model().objects.exclude(schema_name='public')[:1]:
    with schema_context(t.schema_name):
        from intgest_ped.<app>.models import NewModel
        print(f'{t.schema_name}: {NewModel.objects.count()} rows')
"
```

For richer cross-schema queries, use the PostgreSQL MCP tools described below.

## PostgreSQL MCP Tools

The VS Code PostgreSQL extension exposes MCP tools useful during the migration lifecycle — schema inspection before writing, and row-level verification after applying.

> **Server name**: The agent frontmatter declares `postgresql-mcp/*`. This must match the server name registered by the VS Code PostgreSQL extension. If tools are unavailable, verify the correct name in VS Code via **Chat diagnostics view → MCP Servers**.

> **⚠️ Allowed connection only**: Use **`container local`** exclusively. All other profiles are production/staging — never connect to them.

### Connection Lifecycle

```
# 1. List profiles — find the container local profileId
pgsql_list_connection_profiles()

# 2. Connect — capture the returned connectionId
connectionId = pgsql_connect(profileId="<container_local_profile_id>")

# 3+5. Inspect / verify using connectionId (see sections below)

# 6. Disconnect when finished
pgsql_disconnect(connectionId=connectionId)
```

### Inspecting the Schema Before Writing

Always call `pgsql_db_context` before writing a migration to avoid acting on a stale mental model (e.g., a column that already exists, or an index that was already created):

```
# All objects
pgsql_db_context(connectionId=connectionId, objectType="all")

# Tables only (faster for field checks)
pgsql_db_context(connectionId=connectionId, objectType="tables", schemaName="<tenant_schema>")

# Indexes (before adding potentially redundant indexes)
pgsql_db_context(connectionId=connectionId, objectType="indexes", schemaName="<tenant_schema>")
```

Omit `schemaName` to inspect across all schemas. For FK/M2M migrations, also visualise existing relationships:

```
pgsql_visualize_schema(connectionId=connectionId)
```

### Verifying Results After Applying

Use `pgsql_query` (read-only). Never use `pgsql_modify` to apply schema changes — that bypasses the migration system.

```python
pgsql_query(
    connectionId=connectionId,
    queryName="Verify backfill row count",
    queryDescription="Count rows created by the backfill migration in a sample tenant schema",
    query="SELECT COUNT(*) AS total_rows FROM acme.my_new_table",
    validationQueries=[]  # pass [] to skip pre-flight validation
)
```

Common post-migration checks:

| Goal | Approach |
|------|----------|
| Row count in new table | `SELECT COUNT(*) FROM <schema>.<table>` via `pgsql_query` |
| No NULLs in required column | `SELECT COUNT(*) FROM <schema>.<table> WHERE <col> IS NULL` via `pgsql_query` |
| Spot-check migrated FK links | `SELECT * FROM <schema>.<table> WHERE id = <sample_id>` via `pgsql_query` |
| Confirm index was created | `pgsql_db_context(objectType="indexes")` — no SQL needed |

Use `pgsql_open_script` for multi-statement queries or when iterating interactively; use `pgsql_query` for single-statement, one-shot verification.

```
pgsql_open_script(connectionId=connectionId, script="SELECT ...")
```

### What NOT to Use

| Tool | Reason |
|------|--------|
| `pgsql_modify` | Bypasses the migration system — never use for schema changes |
| `pgsql_bulk_load_csv` | Data loading belongs in a data migration |
| Any non-`container local` profile | Production/staging — forbidden |

## Rollback Strategy

### Schema Migration Rollback

```bash
# Revert to a specific previous migration
python manage.py migrate_schemas <app_name> <previous_migration_number>

# Example: revert 0045 back to 0044
python manage.py migrate_schemas files 0044
```

### Data Migration Rollback

Write a `reverse_migration` for any data migration that is not trivially reversible:

```python
def reverse_migration(apps, schema_editor):
    from django_tenants.utils import schema_context, get_tenant_model

    TenantModel = get_tenant_model()

    for tenant in TenantModel.objects.exclude(schema_name='public'):
        with schema_context(tenant.schema_name):
            MyModel = apps.get_model('app_name', 'MyModel')
            MyModel.objects.filter(migrated=True).delete()

class Migration(migrations.Migration):
    operations = [
        migrations.RunPython(forward_migration, reverse_migration, atomic=True),
    ]
```

Use `migrations.RunPython.noop` as the reverse only when the forward operation populates a brand-new table that would be dropped on rollback anyway.

### Emergency Recovery

```bash
# Mark a migration as applied without running it
# (use only when the DB is already in the expected state)
python manage.py migrate_schemas <app_name> <migration_number> --fake

# Mark as unapplied
python manage.py migrate_schemas <app_name> <previous_migration> --fake
```

> **Warning**: `--fake` skips execution. Use it only when the database is already in the expected state but the Django migration record is wrong. Never use it to skip a migration that has not been applied.