# Backend-сервис гибридного поиска сертификатов и деклараций соответствия

## Краткое описание проекта

Этот проект представляет собой backend-сервис для поиска сертификатов и деклараций соответствия по открытым данным Росаккредитации.

Сервис умеет:

- загружать данные из архивов открытых данных Росаккредитации;
- распаковывать `.7z`-архивы;
- импортировать CSV-файлы в PostgreSQL;
- формировать `search_text` для документов;
- создавать embeddings через `sentence-transformers`;
- выполнять классический, семантический и гибридный поиск;
- формировать RAG-объяснение через GigaChat.

Проект построен на `FastAPI`, `PostgreSQL` и `pgvector`. Для локальной разработки база данных поднимается через `Docker Compose`.

> Все команды в README предполагают запуск из корня проекта.

## Возможности проекта

- импорт данных из CSV;
- распаковка `.7z`;
- единый сценарий `import_archive`;
- классический поиск;
- семантический поиск;
- гибридный поиск;
- RAG-объяснение;
- MCP tools layer;
- health-check.

## Стек технологий

Ниже перечислены фактически используемые технологии проекта.

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- Alembic
- Pydantic
- sentence-transformers
- GigaChat
- Docker / Docker Compose
- py7zr
- requests

## Структура проекта

- `backend/api` — REST endpoint-ы.
- `backend/schemas` — Pydantic-схемы запросов и ответов.
- `backend/services` — бизнес-логика импорта, поиска, embeddings и RAG.
- `backend/repositories` — работа с базой данных через SQLAlchemy.
- `backend/db/models` — SQLAlchemy-модели таблиц.
- `backend/external` — внешние клиенты и интеграции: архивы, embeddings, LLM, CSV mapping.
- `backend/mcp` — подготовленный MCP tools layer.
- `scripts` — ручные скрипты для импорта, распаковки и генерации embeddings.
- `alembic` — миграции базы данных.
- `backend/data` — тестовые, скачанные и распакованные данные.

Основные подпапки `backend/data`:

- `backend/data/samples` — sample CSV и тестовые архивы.
- `backend/data/samples/archives` — `.7z`-архивы для локальной проверки.
- `backend/data/extracted` — результаты распаковки архивов.
- `backend/data/raw` — место для исходных файлов.

## Подготовка окружения

Перед запуском установите зависимости:

```bash
pip install -r requirements.txt
```

## Переменные окружения

Пример `.env` для локальной разработки:

```env
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5433
DB_NAME=reestr_pro_db
DEBUG=True

GIGACHAT_CREDENTIALS=your_gigachat_authorization_key
GIGACHAT_MODEL=GigaChat
GIGACHAT_VERIFY_SSL_CERTS=False
```

Безопасный шаблон переменных можно взять из `.env.example`.

Важно:

- `.env` не должен попадать в Git.
- `GIGACHAT_CREDENTIALS` нужно получить в личном кабинете GigaChat.
- `GIGACHAT_VERIFY_SSL_CERTS=False` допустимо только для локальной разработки.

## Запуск PostgreSQL + pgvector через Docker

База данных запускается через [`docker-compose.yml`](docker-compose.yml).

Запуск:

```bash
docker compose up -d
```

Проверка, что контейнер поднят:

```bash
docker ps
```

Остановка без удаления данных:

```bash
docker compose down
```

Важно:

- не используйте `docker compose down -v` без необходимости;
- флаг `-v` удаляет volume с данными PostgreSQL.

## Применение миграций

После запуска базы примените миграции:

```bash
alembic upgrade head
```

Миграции создают таблицы проекта, включая `import_batches`, `registry_documents` и `document_embeddings`, а также включают расширение `vector` для работы `pgvector`.

## Подготовка тестовых данных

Тестовые архивы лежат в:

```text
backend/data/samples/archives/
```

Примеры:

```text
backend/data/samples/archives/declaration_sample.7z
backend/data/samples/archives/certificates_sample.7z
```

Если нужно пересоздать тестовые архивы, используйте:

```bash
python -m scripts.create_test_archive
```

## Единый импорт архива

Скрипт `import_archive` выполняет полный сценарий: архив -> распаковка -> импорт -> embeddings.

Импорт деклараций:

```bash
python -m scripts.import_archive --archive backend/data/samples/archives/declaration_sample.7z --type declaration --limit 1
```

Импорт сертификатов:

```bash
python -m scripts.import_archive --archive backend/data/samples/archives/certificates_sample.7z --type certificate --limit 1
```

Что делает команда:

- распаковывает архив;
- находит CSV-файл;
- импортирует данные в PostgreSQL;
- создаёт embeddings для документов текущего `import_batch`.

## Генерация embeddings отдельно

Если документы уже импортированы, но embeddings ещё не созданы, используйте:

```bash
python -m scripts.generate_embeddings --limit 10
```

Скрипт выбирает документы с заполненным `search_text` и создаёт embeddings только для тех записей, для которых embedding текущей модели ещё отсутствует.

## Запуск FastAPI

Из корня проекта приложение запускается так:

```bash
uvicorn backend.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Основные endpoint-ы

### GET /health

Проверка, что API запущено.

Пример ответа:

```json
{
  "status": "ok"
}
```

Дополнительно есть `GET /health/db` для проверки подключения к базе.

### GET /documents/{document_id}

Возвращает карточку документа по его идентификатору.

Пример:

```text
GET /documents/1
```

### POST /search

Классический поиск по полям таблицы `registry_documents`.

Пример запроса:

```json
{
  "query": "ЛЮКС ТРЕЙД",
  "limit": 10,
  "offset": 0
}
```

Дополнительно поддерживаются поля `document_type` и `status`.

### POST /semantic-search

Семантический поиск по embeddings через `pgvector`.

Пример запроса:

```json
{
  "query": "детская одежда",
  "limit": 5
}
```

Для этого endpoint-а embeddings должны быть заранее созданы.

### POST /hybrid-search

Гибридный поиск, который объединяет классический и семантический результаты в общий список с `final_score`.

Пример запроса:

```json
{
  "query": "детская одежда",
  "document_type": "certificate",
  "limit": 5
}
```

При необходимости можно передать `status`.

### POST /ask

RAG endpoint для ответа на вопрос пользователя по найденным документам.

Пример запроса:

```json
{
  "question": "Найди документ на детскую одежду и объясни, почему он подходит",
  "limit": 3
}
```

Ответ включает текст объяснения и список `sources`.

## RAG и LLM

Endpoint `/ask` работает по следующей схеме:

- выполняет гибридный поиск по вопросу пользователя;
- превращает найденные документы в текстовый контекст;
- передаёт вопрос и контекст в GigaChat;
- возвращает ответ вместе со списком `sources`.

Качество ответа зависит от того, насколько релевантные документы были найдены и насколько корректно LLM интерпретировала контекст.

## MCP tools layer

В проекте реализован read-only слой инструментов для дальнейшего подключения MCP.

Сейчас доступны:

- `search_registry` — выполняет гибридный поиск по реестру;
- `get_document_card` — возвращает карточку документа.

Важно:

- инструменты работают только на чтение;
- они используют уже существующую бизнес-логику backend-сервиса;
- официальный MCP SDK не встроен в основной FastAPI-проект из-за конфликта зависимостей `Starlette/FastAPI`;
- текущий слой подготовлен для дальнейшего подключения полноценного MCP-сервера.

## Полезные скрипты

| Скрипт | Назначение |
| --- | --- |
| `scripts/download_archive.py` | Скачивание `.7z` архива по прямой ссылке |
| `scripts/import_archive.py` | Полный сценарий: архив -> импорт -> embeddings |
| `scripts/import_data.py` | Импорт CSV в PostgreSQL |
| `scripts/extract_archive.py` | Распаковка `.7z` |
| `scripts/generate_embeddings.py` | Генерация embeddings для уже импортированных документов |
| `scripts/create_test_archive.py` | Создание тестовых архивов из sample CSV |
| `scripts/dev/check_embedding_client.py` | Проверка `EmbeddingClient` и размерности вектора |
| `scripts/dev/check_semantic_search.py` | Проверка semantic search на тестовом запросе |

## Ограничения MVP

Текущая версия проекта имеет несколько осознанных ограничений:

- используются тестовые фрагменты данных;
- сервисная защита от дублей по `document_type + document_number` реализована на уровне `ImportService`;
- уникального ограничения на уровне БД для этих полей пока нет;
- MCP пока представлен как подготовленный tools layer;
- GigaChat требует внешний API-ключ;
- качество RAG-ответа зависит от найденных документов и качества LLM;
- автоматический поиск актуальных ссылок на сайте Росаккредитации не реализован;
- реализована загрузка архива по прямой ссылке;
- полноценная автоматическая загрузка актуальных архивов Росаккредитации может быть добавлена отдельно.

## Быстрый сценарий запуска

Минимальная последовательность команд:

```bash
docker compose up -d
alembic upgrade head
python -m scripts.create_test_archive
python -m scripts.import_archive --archive backend/data/samples/archives/declaration_sample.7z --type declaration --limit 1
python -m scripts.import_archive --archive backend/data/samples/archives/certificates_sample.7z --type certificate --limit 1
uvicorn backend.main:app --reload
```

## Как остановить проект

Остановить API:

```text
Ctrl + C
```

Остановить Docker-контейнер без удаления данных:

```bash
docker compose down
```

Не использовать без необходимости:

```bash
docker compose down -v
```

Команда `docker compose down -v` удаляет volume с данными PostgreSQL.
