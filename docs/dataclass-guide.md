> ⚠️ Legacy reference: inherited from another project. Not primary guidance for this hackathon MVP.
> Use `docs/README.md`, `RULES.md`, and `PRODUCT.md` first.

# Dataclass Patterns Guide

Detailed dataclass examples for IntGestPED. For rules and conventions, see [.github/instructions/dataclass-patterns.instructions.md](../.github/instructions/dataclass-patterns.instructions.md).

## BaseDict

All application dataclasses extend `BaseDict` which provides `from_dict` and `to_dict`. Add validation in `__post_init__`:

```python
from dataclasses import dataclass, field
from intgest_ped.util.data_structures.dataclasses import BaseDict

@dataclass
class ExpenditureData(BaseDict):
    valor: Decimal
    data: date
    descricao: str
    
    def __post_init__(self) -> None:
        if self.valor <= 0:
            raise ValueError("valor must be positive")
        if self.data > date.today():
            raise ValueError("data cannot be in the future")
```

Validation runs automatically when the dataclass is instantiated via `__post_init__`.

## Common Validators

No centralised validator utilities exist. Validate inline in `__post_init__`, raising `ValueError` with a descriptive message:

```python
@dataclass
class ItemData(BaseDict):
    quantity: int
    price: Decimal
    name: str
    
    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError(f"quantity must be positive, got {self.quantity}")
        if self.price <= 0:
            raise ValueError(f"price must be positive, got {self.price}")
        if not self.name.strip():
            raise ValueError("name must not be empty")
```

## from_dict Pattern

```python
@dataclass
class CommitmentData(BaseDict):
    numero: str
    valor: Decimal
    favorecido: str
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CommitmentData':
        return cls(
            numero=data['numero'],
            valor=Decimal(str(data['valor'])),
            favorecido=data['favorecido'],
        )
```

## from_request Pattern

```python
@dataclass
class FilterParams(BaseDict):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    
    @classmethod
    def from_request(cls, request) -> 'FilterParams':
        return cls(
            start_date=parse_date(request.GET.get('start_date')),
            end_date=parse_date(request.GET.get('end_date')),
            status=request.GET.get('status'),
        )
    
    def __post_init__(self) -> None:
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("start_date must be before end_date")
```

## Nested Dataclass Instantiation

```python
@dataclass
class Address(BaseDict):
    street: str
    city: str
    state: str

@dataclass
class PersonData(BaseDict):
    name: str
    address: Address
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PersonData':
        return cls(
            name=data['name'],
            address=Address.from_dict(data['address']),  # Nested instantiation
        )
```

## Dataclass with Field Metadata

```python
@dataclass
class ExtractionResult(BaseDict):
    """Result of document extraction with metadata."""
    raw_text: str
    extracted_fields: dict = field(default_factory=dict)
    confidence: float = field(default=0.0)
    errors: list = field(default_factory=list)
    
    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
```

## Using with Optional Fields

```python
from typing import Optional

@dataclass
class DocumentRef(BaseDict):
    doc_type: str
    doc_number: str
    year: int
    entity_id: Optional[int] = None
    budget_unit_id: Optional[int] = None
    
    @property
    def full_reference(self) -> str:
        return f"{self.doc_type}-{self.doc_number}/{self.year}"
```

## Testing Dataclass Validation

```python
class TestExpenditureData(TestCase):
    def test_valid_data(self):
        data = ExpenditureData(valor=Decimal('100.00'), data=date.today(), descricao='Test')
        self.assertEqual(data.valor, Decimal('100.00'))
    
    def test_negative_valor_raises(self):
        with self.assertRaises(ValueError):
            ExpenditureData(valor=Decimal('-1'), data=date.today(), descricao='Test')
    
    def test_from_dict(self):
        raw = {'valor': '100.00', 'data': '2024-01-01', 'descricao': 'Test'}
        data = ExpenditureData.from_dict(raw)
        self.assertIsInstance(data, ExpenditureData)
```

## BaseModel (for API responses)

```python
from external_apis_integration.bases.dataclasses import BaseModel

@dataclass
class ApiItem(BaseModel):
    """For external API response deserialization."""
    id: str
    name: str
    status: str
    
    # BaseModel provides from_dict automatically
    # Usage: item = ApiItem.from_dict(response_json)
```