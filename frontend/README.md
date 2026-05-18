# ReestrPro Frontend

Одностраничный интерфейс для AI-поиска сертификатов и деклараций соответствия через существующий FastAPI backend.

## Запуск

1. Запустить backend:

```bash
uvicorn backend.main:app --reload
```

2. Перейти во frontend:

```bash
cd frontend
```

3. Установить зависимости:

```bash
npm install
```

4. Запустить dev-сервер:

```bash
npm run dev
```

5. Открыть адрес, который покажет Vite.

## Переменные окружения

По умолчанию frontend обращается напрямую к backend по адресу:

```text
http://127.0.0.1:8000
```

Backend должен быть запущен отдельно через:

```bash
uvicorn backend.main:app --reload
```

Пример файла окружения:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Для локальной разработки backend разрешает CORS для `http://127.0.0.1:5173`, `http://localhost:5173`, `http://127.0.0.1:4173` и `http://localhost:4173`.

## Что использует frontend

- `GET /health` для индикатора доступности backend.
- `POST /ask` для основного RAG-сценария.

Обычный поиск (`/search`, `/semantic-search`, `/hybrid-search`) отдельными страницами не реализован, потому что основной сценарий интерфейса - объяснение ответа через `POST /ask`.

История запросов не сохраняется.
