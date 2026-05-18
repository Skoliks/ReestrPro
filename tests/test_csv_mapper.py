from datetime import date

from backend.external.csv_mapper import map_row_to_document_data, parse_first_date


def test_map_declaration_row_to_document_data():
    row = {
        "id": "test-declaration-1",
        "Статус": "Архивный",
        "Номер ДС": "ЕАЭС N RU Д-RU.РА07.А.63018/25",
        "Дата рег": "2025-08-29",
        "Срок действия": "2026-01-01",
        "Тех регламенты": "О безопасности пищевой продукции",
        "Заявитель": "Плахотя Николай Николаевич",
        "ИНН Заявителя": "1234567890",
        "ОГРН Заявителя": "1234567890123",
        "Изготовитель": "Плахотя Николай Николаевич",
        "ИНН производителя": "1234567890",
        "ОГРН изготовителя": "1234567890123",
        "Полное наименование": "Плодоовощная продукция",
        "Коды ОКПД2 / ТНВЭД": "1212918000",
    }

    result = map_row_to_document_data(
        row=row,
        document_type="declaration",
        import_batch_id=1,
    )

    assert result["import_batch_id"] == 1
    assert result["source_document_id"] == "test-declaration-1"
    assert result["document_type"] == "declaration"
    assert result["document_number"] == "ЕАЭС N RU Д-RU.РА07.А.63018/25"
    assert result["status"] == "Архивный"
    assert result["applicant_name"] == "Плахотя Николай Николаевич"
    assert result["manufacturer_name"] == "Плахотя Николай Николаевич"
    assert result["product_full_name"] == "Плодоовощная продукция"
    assert result["product_codes"] == "1212918000"
    assert "Плодоовощная продукция" in result["search_text"]
    assert "ЕАЭС N RU Д-RU.РА07.А.63018/25" in result["search_text"]


def test_parse_first_date_returns_first_date_from_semicolon_list():
    assert parse_first_date("2021-01-28; 2020-12-15") == date(2021, 1, 28)


def test_parse_first_date_parses_dd_mm_yyyy():
    assert parse_first_date("18.10.2024") == date(2024, 10, 18)


def test_parse_first_date_returns_none_for_empty_value():
    assert parse_first_date("") is None
    assert parse_first_date(None) is None


def test_map_declaration_row_keeps_long_product_full_name() -> None:
    long_name = ("Очень длинное наименование продукции " * 12).strip()

    row = {
        "id": "test-declaration-long-name",
        "Статус": "Архивный",
        "Номер ДС": "DECL-LONG-001",
        "Полное наименование": long_name,
    }

    result = map_row_to_document_data(
        row=row,
        document_type="declaration",
        import_batch_id=1,
    )

    assert result["product_full_name"] == long_name
    assert len(result["product_full_name"]) > 255
