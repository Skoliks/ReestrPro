from backend.external.csv_mapper import map_row_to_document_data


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