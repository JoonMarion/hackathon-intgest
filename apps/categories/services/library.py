from apps.categories.models import Category


def build_category_library_context(categories: list[Category]) -> dict[str, object]:
    income_categories = [
        category for category in categories if category.kind == Category.Kind.INCOME
    ]
    expense_categories = [
        category for category in categories if category.kind == Category.Kind.EXPENSE
    ]

    return {
        "income_categories": income_categories,
        "expense_categories": expense_categories,
        "category_summary": {
            "total_count": len(categories),
            "income_count": len(income_categories),
            "expense_count": len(expense_categories),
            "has_both_kinds": bool(income_categories and expense_categories),
            "newest_category": categories[0] if categories else None,
        },
    }