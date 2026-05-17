# Scripts

В этой папке находятся вспомогательные скрипты для разработки и ручного запуска отдельных операций проекта.

Скрипты используются для:

- скачивания архивов по прямой ссылке;
- создания тестовых архивов;
- распаковки `.7z` архивов;
- импорта CSV-файлов в базу данных;
- проверки работы маппера и репозиториев во время разработки.

Все команды нужно запускать из корня проекта.

---

## `import_data.py`

Скрипт импортирует CSV-файл с декларациями или сертификатами в PostgreSQL.

Использует:

- `ImportService`;
- `csv_mapper`;
- `DocumentRepository`;
- `ImportBatchRepository`.

### Импорт деклараций

```powershell
python -m scripts.import_data --file backend/data/extracted/declarations/declaration_sample.csv --type declaration --limit 1
````

### Импорт сертификатов

```powershell
python -m scripts.import_data --file backend/data/extracted/certificates/certificates_sample.csv --type certificate --limit 1
```

### Аргументы

```text
--file   путь к CSV-файлу
--type   тип документа: declaration или certificate
--limit  количество строк для импорта
```

Если `--limit` не указан, скрипт попытается импортировать весь файл.

---

## `download_archive.py`

Скрипт скачивает `.7z` архив по прямой ссылке и сохраняет его в указанную папку.

Использует функцию:

```text
backend/external/fsa_client.py
```

### Пример запуска

```powershell
python -m scripts.download_archive --url "ССЫЛКА_НА_АРХИВ.7z" --output backend/data/raw/declarations/declaration.7z
```

После скачивания следующий шаг:

```powershell
python -m scripts.import_archive --archive backend/data/raw/declarations/declaration.7z --type declaration --limit 100
```

### Аргументы

```text
--url     прямая ссылка на .7z архив
--output  путь, куда нужно сохранить архив
```

---

## `extract_archive.py`

Скрипт распаковывает `.7z` архив в указанную папку.

Использует функцию `extract_7z_archive` из модуля:

```text
backend/external/archive_extractor.py
```

### Распаковка архива с декларациями

```powershell
python -m scripts.extract_archive --archive backend/data/samples/archives/declaration_sample.7z --output backend/data/extracted/declarations
```

### Распаковка архива с сертификатами

```powershell
python -m scripts.extract_archive --archive backend/data/samples/archives/certificates_sample.7z --output backend/data/extracted/certificates
```

### Аргументы

```text
--archive  путь к .7z архиву
--output   папка, куда нужно распаковать архив
```

---

## `create_test_archive.py`

Скрипт создаёт тестовые `.7z` архивы из sample CSV-файлов.

Нужен только для локальной разработки и проверки распаковки архивов.

### Пример запуска

```powershell
python -m scripts.create_test_archive
```

После запуска создаются архивы:

```text
backend/data/samples/archives/declaration_sample.7z
backend/data/samples/archives/certificates_sample.7z
```

---

## `check_mapper.py`

Проверочный скрипт для `csv_mapper`.

Он читает одну строку CSV-файла и показывает, как она преобразуется в данные для модели `RegistryDocument`.

Используется для проверки:

* номера документа;
* статуса;
* дат;
* заявителя;
* изготовителя;
* продукции;
* `search_text`.

### Пример запуска

```powershell
python -m scripts.dev.check_mapper
```

Скрипт нужен только для разработки. В основной логике проекта он не используется.

---

## `check_repository.py`

Проверочный скрипт для репозиториев.

Он создаёт тестовый `ImportBatch`, тестовый `RegistryDocument`, сохраняет их в базу данных и проверяет получение документа по id.

### Пример запуска

```powershell
python -m scripts.dev.check_repository
```

Внимание: скрипт создаёт тестовые записи в базе данных. После проверки их можно удалить вручную через SQL.

Пример удаления тестовых данных:

```sql
DELETE FROM registry_documents
WHERE document_number = 'TEST-123';

DELETE FROM import_batches
WHERE source_file_name = 'test.csv';
```

---

## Рекомендуемый порядок проверки первой итерации

### 1. Создать тестовые архивы

```powershell
python -m scripts.create_test_archive
```

### 2. Распаковать архив деклараций

```powershell
python -m scripts.extract_archive --archive backend/data/samples/archives/declaration_sample.7z --output backend/data/extracted/declarations
```

### 3. Распаковать архив сертификатов

```powershell
python -m scripts.extract_archive --archive backend/data/samples/archives/certificates_sample.7z --output backend/data/extracted/certificates
```

### 4. Импортировать декларации

```powershell
python -m scripts.import_data --file backend/data/extracted/declarations/declaration_sample.csv --type declaration --limit 1
```

### 5. Импортировать сертификаты

```powershell
python -m scripts.import_data --file backend/data/extracted/certificates/certificates_sample.csv --type certificate --limit 1
```

---

## Примечание

Все скрипты запускаются из корня проекта, например:

```text
VKR/
├── backend/
├── scripts/
├── requirements.txt
└── README.md
```

Правильный пример запуска:

```powershell
python -m scripts.import_data --file backend/data/extracted/declarations/declaration_sample.csv --type declaration --limit 1
```

Неправильный пример запуска:

```powershell
python scripts/import_data.py
```

В проекте предпочтительно использовать запуск через `python -m`, чтобы корректно работали импорты из пакета `backend`.

```
```

docker compose up -d
alembic upgrade head

python -m scripts.import_archive --archive backend/data/samples/archives/declaration_sample.7z --type declaration --limit 1
python -m scripts.import_archive --archive backend/data/samples/archives/certificates_sample.7z --type certificate --limit 1

uvicorn backend.main:app --reload
