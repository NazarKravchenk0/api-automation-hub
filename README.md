# API Automation Hub (FastAPI + Postgres + Redis RQ)

Единая точка приема событий и лидов из разных источников (Stripe, Calendly, формы сайта), 
с дедупликацией, бизнес-правилами, очередью задач и минимальным дашбордом.

## Быстрый старт (Docker Compose)
1) Скопируйте `.env.example` в `.env` и при необходимости измените значения.
2) Запустите:
```bash
docker compose up --build
```
3) Документация API: http://localhost:8000/docs
4) Админка БД (Adminer): http://localhost:8080  (System: PostgreSQL; Server: db; User/Pass: из .env; DB: из .env)

## Что внутри
- **FastAPI** — REST API и mini-дашборд
- **PostgreSQL** — хранилище лидов и событий
- **Redis + RQ** — очередь фоновых задач (обогащение, уведомления, ретраи)
- **Бизнес-правила**: нормализация, дедуп по email/телефону, приоритеты источников
- **Вебхуки**: Stripe, Calendly, Generic Form
- **Мониторинг**: healthcheck эндпоинт, структурные логи
- **OpenAPI/Swagger**: автодоки на /docs

## Переменные окружения (.env)
Смотрите `.env.example` (подключение к БД, Redis, api-ключи интеграций).

## Основные эндпоинты
- `POST /webhooks/stripe` — события Stripe (invoice.payment_succeeded, checkout.session.completed и т.д.)
- `POST /webhooks/calendly` — события Calendly (invitation.created и т.д.)
- `POST /webhooks/form` — универсальный прием форм (name/email/phone/source/utm)
- `GET  /leads` — список лидов с пагинацией и фильтрами
- `GET  /events` — список событий
- `GET  /metrics` — метрики (кол-во лидов по источникам, CR where applicable)
- `GET  /health` — статус сервиса

## Разработка (локально без Docker)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export $(cat .env.example | xargs)  # для примера
uvicorn app.main:app --reload
rq worker --url $REDIS_URL hub-queue
```
> Для Windows используйте `set`/`$Env:`.

## Тесты
```bash
pytest -q
```

## Замечания по соблюдению правил
Скриптинг и вебхуки должны соответствовать ToS сервисов. Отправка уведомлений/сообщений — только с согласия клиента и в рамках GDPR/локальных законов.
