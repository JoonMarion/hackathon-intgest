> ⚠️ Legacy reference: inherited from another project. Not primary guidance for this hackathon MVP.
> Use `docs/README.md`, `RULES.md`, and `PRODUCT.md` first.

# Code Architecture Patterns

Detailed examples and patterns for IntGestPED code architecture. For rules and conventions, see [.github/instructions/code-architecture.instructions.md](../.github/instructions/code-architecture.instructions.md).

## Current model-layer pattern (MVP)

- Keep shared `Kind` enums in `config/models/choices.py`.
- Keep abstract timestamp base in `config/models/base.py` with `created_at` and `updated_at`.
- Expose shared model primitives through `config/models/__init__.py` for canonical imports.
- Require explicit `class Meta` in domain models.
- Follow project stack conventions: Django 6, Python 3.13, and `uv` commands.

## Type Hints Examples

```python
from typing import List, Optional, Dict
import intgest_ped.util.types.models as type_models

def process_files(
    files: List['type_models.File'],
    user: 'type_models.User',
    options: Optional[Dict[str, str]] = None
) -> bool:
    ...
```

### Type Definitions Location

Type definitions are in `intgest_ped/util/types/`:

```python
# intgest_ped/util/types/models.py
from typing import TYPE_CHECKING
from django.db.models import Manager, QuerySet

if TYPE_CHECKING:
    from account.models import User
    from intgest_ped.files.models import File

# Type aliases for QuerySets and Managers
FileQS = QuerySet["File"]
FileManager = Manager["File"]
UserQS = QuerySet["User"]
```

Usage:

```python
import intgest_ped.util.types.models as type_models

def get_user_files(user: 'type_models.User') -> 'type_models.FileQS':
    return user.file_set.all()
```

## LazyModels Pattern

```python
# intgest_ped/util/lazy_models.py
from django.apps import apps
from django.utils.functional import SimpleLazyObject
from typing import cast
from intgest_ped.util import types

class LazyModels:
    # NOTE: cast('types.X', ...) is valid here only because `types` is imported
    # in _this_ module. In other files, use 'type_models.User' with
    # `import intgest_ped.util.types.models as type_models` instead.
    User = cast('types.User', _glm('account', 'User'))
    File = cast('types.File', _glm('files', 'File'))
    Entity = cast('types.Entity', _glm('base', 'Entity'))
    # ... more models
```

### Usage

```python
# ✅ Good - Using LazyModels
from intgest_ped.util.lazy_models import LazyModels

def my_service_function():
    files = LazyModels.File.objects.filter(status='active')
    entity = LazyModels.Entity.objects.get()
    return files

# ❌ Bad - Direct model import in services/tasks
from intgest_ped.files.models import File  # Can cause circular imports
```

## Service Architecture

### Service Folder Structure

```
intgest_ped/
├── files/
│   └── services/
│       ├── sign_documents_processor/
│       │   ├── __init__.py
│       │   ├── processor.py      # Main service class
│       │   ├── queries.py        # Database queries (isolated)
│       │   └── map_builder.py    # Data mapping/transformation
│       ├── expense_process_builder/
│       │   ├── builder.py        # Main builder logic
│       │   ├── dataclasses.py    # Data structures (isolated)
│       │   ├── queries.py        # Database queries (isolated)
│       │   ├── data_extract.py   # Data extraction logic
│       │   └── tree_organize.py  # Tree structure logic
│       └── files_import_from_email/
│           ├── file_import_from_email.py  # Main service
│           ├── dataclasses.py    # Data structures
│           ├── queries.py        # Database queries
│           └── auth.py           # Authentication logic
```

### Service Module Isolation Pattern

| File | Purpose | Contains |
|------|---------|----------|
| `dataclasses.py` | Data structures | `@dataclass`, `NamedTuple`, `Enum`, result types |
| `queries.py` | Database access | QuerySet factories, filters, annotations |
| `processor.py` / `builder.py` | Main logic | Primary service class |
| `map_builder.py` | Data mapping | Dict/object transformations |
| `data_fetcher.py` | External data | API calls, external integrations |
| `auth.py` | Authentication | Credential handling, auth configs |

> **Note**: Some existing files use `querys.py` (incorrect spelling). New files should use `queries.py`.

### queries.py Pattern

```python
from django.db.models import Q
from django.utils.functional import cached_property
from intgest_ped.util.lazy_models import LazyModels
import intgest_ped.util.types.models as type_models

class MyServiceQueries:
    """Database queries for MyService."""
    
    @cached_property
    def base_queryset(self):
        return LazyModels.File.objects.select_related('doc_type')
    
    def get_files_by_status(self, status: str) -> 'type_models.FileQS':
        return self.base_queryset.filter(status=status)
    
    def get_files_for_processing(self, user: 'type_models.User') -> 'type_models.FileQS':
        return self.base_queryset.filter(
            Q(owner=user) | Q(management_unit__in=user.management_units.all())
        ).exclude(processed=True)
```

### dataclasses.py Pattern

```python
from dataclasses import dataclass, field, asdict
from typing import List, Optional, NamedTuple
from enum import Enum
from datetime import date

class ProcessingStatus(Enum):
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    FAILED = 'failed'

class DocumentRecord(NamedTuple):
    file_hash: str
    document_id: str
    processed_at: date

@dataclass
class ProcessingResult:
    success: bool = False
    status: ProcessingStatus = ProcessingStatus.PENDING
    processed_files: List[DocumentRecord] = field(default_factory=list)
    error_message: str = ''
    
    def to_dict(self):
        return asdict(self)
```

### Complete Service Example

```python
# __init__.py
from .processor import MyServiceProcessor

# processor.py
from typing import List
from intgest_ped.util.lazy_models import LazyModels
import intgest_ped.util.types.models as type_models
from .queries import MyServiceQueries
from .dataclasses import ProcessingResult, ProcessingStatus

class MyServiceProcessor:
    def __init__(self, user: 'type_models.User'):
        self.user = user
        self.queries = MyServiceQueries()
    
    def process(self) -> ProcessingResult:
        result = ProcessingResult()
        files = self.queries.get_files_for_processing(self.user)
        for file in files:
            try:
                self._process_file(file)
            except Exception as e:
                result.error_message = str(e)
                result.status = ProcessingStatus.FAILED
                return result
        result.success = True
        result.status = ProcessingStatus.COMPLETED
        return result
    
    def _process_file(self, file: 'type_models.File') -> None:
        ...
```

## Task Architecture

### Task Examples

```python
# ✅ Good - Task delegates to service
from celery import shared_task
from intgest_ped.util.lazy_models import LazyModels
from intgest_ped.files.services.sign_documents_processor import SignDocumentsProcessor

@shared_task
def send_file_to_sign_task(user_pk: int, file_uuid: str):
    file = LazyModels.File.objects.select_related('doc_type', 'management_unit').get(pk=file_uuid)
    user = LazyModels.User.objects.get(pk=user_pk)
    processor = SignDocumentsProcessor(user=user)
    success, msg = processor.process_file(file=file)
    if not success:
        logger.error("Error sending '%s' to sign: %s", file, msg)

# ❌ Bad - Business logic in task
@shared_task
def send_file_to_sign_task(user_pk: int, file_uuid: str):
    file = File.objects.get(pk=file_uuid)
    # 100+ lines of business logic - DON'T do this!
```

### Task Locking Pattern

> **Note**: The raw `cache.get`/`cache.set` pattern below is legacy. Keep this section as historical reference only for inherited code.

```python
# Preferred pattern (use this for new code):
from sso_integration.utils.redis import redis_lock

@shared_task
def do_import_tce_structure_task(pk: str):
    with redis_lock(RedisLockIds.IMPORT_TCE_STRUCTURE):
        service = TCEStructureImporter()
        service.import_structures(pk)
```

```python
# Legacy pattern (avoid in new code):
from django.core.cache import cache

@shared_task
def do_import_tce_structure_task(pk: str):
    cache_key = f'import_tce_structure_{pk}'
    if cache.get(cache_key):
        return logger.info(f'Import {pk} already in progress.')
    cache.set(cache_key, True, timeout=3600)
    try:
        service = TCEStructureImporter()
        service.import_structures(pk)
    finally:
        cache.delete(cache_key)
```

### Reference Task Implementations

| Task | Location | Pattern |
|------|----------|---------|
| `send_file_to_sign_task` | `files/tasks.py#L303` | Service delegation |
| `do_import_tce_structure_task` | `entity_structure/tasks.py#L86` | Cache lock + service |
| `extract_train_file_text_task` | `base/tasks.py#L412` | Retry + service |
| `start_process_expense_verification` | `files/tasks.py#L258` | Iterator + services |

## Updates System (BaseUpdater)

```python
from intgest_ped.util.services import BaseUpdater
from intgest_ped.util.lazy_models import LazyModels

class MyDataUpdater(BaseUpdater):
    def execute(self):
        queryset = LazyModels.File.objects.filter(needs_update=True)
        for item in self.tqdm(queryset):
            self.update_item(item)
    
    def update_item(self, item):
        ...
```

Updates are called in `intgest_ped/base/services/full_update.py` and run with `./manage.py updatedb`.

## Future Architecture Plans

### Async Rendering / Progressive Enhancement

When rendering lists that require per-item external HTTP calls (e.g., checking digital signature status from an external API), **never block page render** with N synchronous calls. Instead, use the async status pattern:

#### Backend

- Create a lightweight API endpoint (e.g., `GenericAPIView`) that returns the status for a single object
- Use object-level DRF permissions (`BasePermission.has_object_permission`) — never inline permission checks in the view body

```python
# intgest_ped/portal/views/api.py
class FileSignatureStatusAPIView(GenericAPIView):
    permission_classes = (IsAuthenticated, FileViewPermission)
    queryset = LazyModels.File.objects.all()

    def get(self, request, pk: str):
        obj = self.get_object()
        try:
            ok = bool(obj.ok_signature)
        except Exception:
            logger.exception('Error checking ok_signature for file pk=%s', pk)
            ok = False
        return Response({'ok': ok}, status=status.HTTP_200_OK)
```

#### Template

- Render a neutral/loading state (spinner icon, neutral CSS class)
- Store the fetch URL and CSS class names in `data-*` attributes
- Keep the element wrapped in an `<a href>` for no-JS fallback

```html
<button class="{{ neutral_btn }} effect-zoom js-file-sign-status"
        data-sign-status-url="{% url 'intgest_ped.portal:file-signature-status' object.pk %}"
        data-btn-green-class="{{ green_btn }}"
        data-btn-red-class="{{ red_btn }}"
        data-btn-neutral-class="{{ neutral_btn }}">
    <i class="fa-duotone fa-spinner fa-spin"></i>
</button>
```

#### Frontend JS

- After `DOMContentLoaded`, query all `.js-file-sign-status` buttons and fetch each status
- Swap the spinner icon for the final icon and apply green/red CSS classes
- Handle FontAwesome SVG replacement (see below) — the icon `<i>` may have been replaced with `<svg>` by the time JS runs

> **FontAwesome SVG gotcha**: FontAwesome's JS replaces `<i>` tags with inline `<svg>` elements after DOM load. When dynamically updating icons, always check whether the child is `<i>` or `<svg>` and create a new `<i>` element if needed. See `file-signature-status.js` for a reference implementation.

### Mappers Folder Structure

Forms, serializers, and filtersets should be organized in a `mappers/` folder:

```
intgest_ped/<app>/mappers/
├── __init__.py
├── forms.py
├── serializers.py
└── filtersets.py
```

### App-Based API Structure

The centralized `intgest_ped/api/` app is replaced by per-app `http/` and `api/` packages:

```
intgest_ped/<app>/
├── http/
│   ├── __init__.py
│   ├── views.py        # Django template views and view classes
│   └── forms.py        # Forms used by HTTP views
├── api/
│   ├── __init__.py
│   ├── views.py        # DRF ViewSets
│   └── serializers.py  # DRF serializers
└── mappers/
```

Note: add a canonical aggregator `intgest_ped/<app>/urls.py` that includes both `http.urls` and `api.urls`.