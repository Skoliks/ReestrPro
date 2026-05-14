# Скрипты в проекте простыми словами

## Что такое скрипт

В нашем проекте скрипт это маленькая программа на Python для одной конкретной задачи: запустил, она что-то сделала и завершилась. Это не сервер и не API. Сервер работает постоянно, а скрипт обычно нужен для разового действия.

В текущей итерации скрипты обслуживают pipeline данных: подготовить архив, распаковать его, прочитать CSV, преобразовать строки и сохранить их в PostgreSQL. Это соответствует цели Iteration 1: Data Core.

## Какие скрипты есть

### `scripts/create_test_archive.py`

Нужен только для локальной разработки. Он берёт два sample CSV и упаковывает их в `.7z`.

Что делает внутри:

- проверяет, что исходный CSV-файл существует;
- создаёт папку для архивов, если её ещё нет;
- через `py7zr` создаёт `.7z` архив.

Запуск:

```powershell
python -m scripts.create_test_archive
```

После запуска создаются архивы:

- `backend/data/samples/archives/declaration_sample.7z`
- `backend/data/samples/archives/certificates_sample.7z`

### `scripts/extract_archive.py`

Этот скрипт распаковывает `.7z` архив в указанную папку.

Что делает внутри:

- принимает путь к архиву через `--archive`;
- принимает папку назначения через `--output`;
- вызывает функцию `extract_7z_archive` из `backend/external/archive_extractor.py`;
- проверяет, что архив существует;
- создаёт папку назначения;
- распаковывает все файлы из архива.

Запуск:

```powershell
python -m scripts.extract_archive --archive backend/data/samples/archives/declaration_sample.7z --output backend/data/extracted/declarations
```

Или для сертификатов:

```powershell
python -m scripts.extract_archive --archive backend/data/samples/archives/certificates_sample.7z --output backend/data/extracted/certificates
```

### `scripts/import_data.py`

Это главный скрипт первой итерации. Он импортирует CSV в базу данных PostgreSQL.

Какие аргументы принимает:

- `--file` — путь к CSV-файлу;
- `--type` — тип документа: `declaration` или `certificate`;
- `--limit` — сколько строк импортировать.

Пример запуска:

```powershell
python -m scripts.import_data --file backend/data/extracted/declarations/declaration_sample.csv --type declaration --limit 10
```

Что происходит внутри по шагам:

1. Python запускает модуль `scripts.import_data`.
2. Скрипт читает аргументы командной строки.
3. Создаётся подключение к базе через `SessionLocal`.
4. Создаётся `ImportService`.
5. `ImportService` создаёт запись `import_batch`.
6. CSV читается построчно через `csv.DictReader`.
7. Каждая строка передаётся в `csv_mapper`.
8. Маппер преобразует строку CSV в данные для `RegistryDocument`.
9. Документ сохраняется в базу через `DocumentRepository`.
10. В `import_batch` обновляется статистика: сколько строк обработано, сколько успешно, сколько с ошибкой.
11. В конце скрипт печатает итог импорта.

Что важно:

- исходная строка CSV сохраняется в поле `raw_data`;
- текст для последующего поиска собирается в поле `search_text`;
- если одна строка падает с ошибкой, импорт не обязательно останавливается полностью, ошибка фиксируется отдельно.

### `scripts/dev/check_mapper.py`

Это отладочный скрипт. Он не сохраняет ничего в базу.

Что делает:

- открывает sample CSV;
- берёт первую строку;
- прогоняет её через `map_row_to_document_data`;
- печатает основные поля результата.

Он нужен, чтобы быстро проверить глазами:

- правильно ли читается номер документа;
- правильно ли читается статус;
- корректно ли парсятся даты;
- что попадает в `search_text`.

Запуск:

```powershell
python -m scripts.dev.check_mapper
```

### `scripts/dev/check_repository.py`

Это второй отладочный скрипт, уже для проверки базы данных и репозиториев.

Что делает:

- создаёт тестовый `ImportBatch`;
- сохраняет его в БД через `ImportBatchRepository`;
- создаёт тестовый `RegistryDocument`;
- сохраняет его через `DocumentRepository`;
- читает документ обратно по `id`;
- печатает результат.

Он нужен, чтобы проверить, что слой работы с базой реально сохраняет и читает данные.

Запуск:

```powershell
python -m scripts.dev.check_repository
```

Важно: этот скрипт создаёт тестовые записи в базе.

## Служебные скрипты Alembic

Кроме папки `scripts/`, в проекте есть ещё служебные миграции Alembic.

### `alembic/env.py`

Этот файл обычно не запускают руками напрямую. Его использует Alembic, когда ты вызываешь команды вроде:

```powershell
alembic upgrade head
```

Что он делает:

- читает настройки БД из `.env`;
- собирает `DATABASE_URL`;
- подцепляет SQLAlchemy metadata;
- подготавливает Alembic к запуску миграций.

### `alembic/versions/fb1563c51059_first_migration.py`

Это уже конкретная миграция.

Что делает:

- `upgrade()` создаёт таблицы `import_batches` и `registry_documents`;
- `downgrade()` удаляет эти таблицы.

То есть миграция нужна для изменения структуры базы данных.

## Как всё связано между собой

Полная цепочка в текущей итерации выглядит так:

1. При необходимости создаём тестовые архивы через `create_test_archive`.
2. Распаковываем `.7z` через `extract_archive`.
3. Импортируем CSV через `import_data`.
4. Если нужно понять преобразование строки, используем `check_mapper`.
5. Если нужно проверить именно запись и чтение из БД, используем `check_repository`.
6. Если нужно создать таблицы в базе, используем Alembic.

## Почему в проекте используют `python -m`

В проекте скрипты лучше запускать так:

```powershell
python -m scripts.import_data --file backend/data/extracted/declarations/declaration_sample.csv --type declaration --limit 1
```

А не так:

```powershell
python scripts/import_data.py
```

Причина простая: запуск через `python -m` помогает Python правильно понимать структуру проекта и корректно работать с импортами вида `from backend...`.

## Коротко по смыслу каждого скрипта

- `create_test_archive.py` — делает тестовые архивы.
- `extract_archive.py` — распаковывает архивы.
- `import_data.py` — загружает CSV в PostgreSQL.
- `check_mapper.py` — показывает, как одна строка CSV превращается в данные документа.
- `check_repository.py` — проверяет, что репозитории умеют сохранять и читать данные из БД.
- `alembic/env.py` и файлы из `alembic/versions/` — служат для управления структурой базы данных.
