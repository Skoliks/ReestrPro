from datetime import date, datetime
from typing import Any


def clean_value(value: Any) -> str | None:
    if value is None:
        return None
    
    value = str(value).strip()
    
    if not value:
        return None
    
    return value


def parse_date(value: Any) -> date | None:
    cleaned_value = clean_value(value)
    
    if cleaned_value is None:
        return None
    
    date_formats = ["%d.%m.%Y", "%Y-%m-%d"]
    
    for date_format in date_formats:
        try:
            return datetime.strptime(value, date_format).date()
        except ValueError:
            continue
    
    return None


def clean_row(row: dict[str, Any]) -> dict[str, str | None]:
    return {key: clean_value(value) for key, value in row.items()}


def get_first_value(row: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = clean_value(row.get(key))
        if value is not None:
            return value
    
    return None

def build_search_text(data: dict[str, Any]) -> str:
    fields = [
        ("Тип документа", data.get("document_type")),
        ("Номер документа", data.get("document_number")),
        ("Статус", data.get("status")),
        ("Заявитель", data.get("applicant_name")),
        ("Изготовитель", data.get("manufacturer_name")),
        ("Продукция", data.get("product_full_name")),
        ("Тип продукции", data.get("product_type")),
        ("Марка", data.get("product_brand")),
        ("Модель", data.get("product_model")),
        ("Артикул", data.get("product_article")),
        ("Коды продукции", data.get("product_codes")),
        ("Технические регламенты", data.get("technical_regulations")),
        ("Испытательная лаборатория", data.get("test_laboratory")),
    ]

    parts = []

    for label, value in fields:
        cleaned_value = clean_value(value)

        if cleaned_value is not None:
            parts.append(f"{label}: {cleaned_value}")

    return "\n".join(parts)


def map_declaration_row(
    row: dict[str, Any],
    import_batch_id: int | None = None,
) -> dict[str, Any]:
    cleaned_row = clean_row(row)

    data: dict[str, Any] = {
        "import_batch_id": import_batch_id,
        "source_document_id": cleaned_row.get("id"),
        "document_type": "declaration",
        "document_number": cleaned_row.get("Номер ДС"),
        "temporary_number": cleaned_row.get("Временный номер декл"),
        "status": cleaned_row.get("Статус"),
        "registered_at": parse_date(cleaned_row.get("Дата рег")),
        "valid_until": parse_date(cleaned_row.get("Срок действия")),
        "technical_regulations": cleaned_row.get("Тех регламенты"),
        "product_group": cleaned_row.get("Группа продукции"),
        "applicant_name": cleaned_row.get("Заявитель"),
        "applicant_inn": cleaned_row.get("ИНН Заявителя"),
        "applicant_ogrn": cleaned_row.get("ОГРН Заявителя"),
        "manufacturer_name": cleaned_row.get("Изготовитель"),
        "manufacturer_inn": cleaned_row.get("ИНН производителя"),
        "manufacturer_ogrn": cleaned_row.get("ОГРН изготовителя"),
        "product_full_name": cleaned_row.get("Полное наименование"),
        "product_type": cleaned_row.get("Тип продукции"),
        "product_brand": cleaned_row.get("Торговая марка"),
        "product_model": cleaned_row.get("Модель"),
        "product_article": cleaned_row.get("Артикул"),
        "product_codes": cleaned_row.get("Коды ОКПД2 / ТНВЭД"),
        "test_laboratory": cleaned_row.get("ИЛ"),
        "test_protocol_date": cleaned_row.get("Дата протокола ИЛ"),
        "test_protocol_number": cleaned_row.get("Номер протокола ИЛ"),
        "raw_data": cleaned_row,
    }

    data["search_text"] = build_search_text(data)

    return data


def map_certificate_row(
    row: dict[str, Any],
    import_batch_id: int | None = None,
) -> dict[str, Any]:
    cleaned_row = clean_row(row)

    data: dict[str, Any] = {
        "import_batch_id": import_batch_id,
        "source_document_id": cleaned_row.get("id"),
        "document_type": "certificate",
        "document_number": cleaned_row.get("Номер СС"),
        "temporary_number": get_first_value(
            cleaned_row,
            "Временный номер СС",
            "Временный номер серт",
        ),
        "status": cleaned_row.get("Статус"),
        "registered_at": parse_date(cleaned_row.get("Дата рег")),
        "valid_until": parse_date(cleaned_row.get("Срок действия")),
        "technical_regulations": cleaned_row.get("Тех регламенты"),
        "product_group": cleaned_row.get("Группа продукции"),
        "applicant_name": cleaned_row.get("Заявитель"),
        "applicant_inn": cleaned_row.get("ИНН заявителя"),
        "applicant_ogrn": cleaned_row.get("ОГРН заявителя"),
        "manufacturer_name": cleaned_row.get("Изготовитель"),
        "manufacturer_inn": cleaned_row.get("ИНН изготовителя"),
        "manufacturer_ogrn": cleaned_row.get("ОГРН изготовителя"),
        "product_full_name": cleaned_row.get("Полное наименование продукции"),
        "product_type": cleaned_row.get("Тип продукции"),
        "product_brand": cleaned_row.get("Марка продукции"),
        "product_model": cleaned_row.get("Модель продукции"),
        "product_article": cleaned_row.get("Артикул продукции"),
        "product_codes": cleaned_row.get("Коды ОКПД2/ТНВЭД"),
        "test_laboratory": cleaned_row.get("ИЛ"),
        "test_protocol_date": cleaned_row.get("Дата протокола ИЛ"),
        "test_protocol_number": cleaned_row.get("Номер протокола ИЛ"),
        "raw_data": cleaned_row,
    }

    data["search_text"] = build_search_text(data)

    return data


def map_row_to_document_data(
    row: dict[str, Any],
    document_type: str,
    import_batch_id: int | None = None,
) -> dict[str, Any]:
    if document_type == "declaration":
        return map_declaration_row(row, import_batch_id)

    if document_type == "certificate":
        return map_certificate_row(row, import_batch_id)

    raise ValueError(f"Unsupported document_type: {document_type}")
