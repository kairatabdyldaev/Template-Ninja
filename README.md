# Template Ninja

Каркас Django-проекта по [pySilver/django-styleguide](https://github.com/pySilver/django-styleguide): тонкий HTTP-слой, Pydantic DTO и бизнес-логика в сервисах.

```
HTTP
 │
 ▼
Ninja          src/config/api.py, src/<domain>/apis.py
 │  API Schema
 ▼
DTO            src/<domain>/schemas.py
 │
 ▼
Service        src/<domain>/services.py
 │  business logic
 ▼
Django ORM     src/<domain>/models.py
 │
 ▼
PostgreSQL
```

Ninja проверяет вход через схему и сразу передаёт его в сервис. Отдельный второй DTO не нужен: схема и есть контракт между API и сервисом. Эндпоинт не содержит бизнес-правил и не обращается к ORM. Список, карточка, создание, обновление и завершение идут через `TaskService`. Отсутствующая задача — `TaskNotFoundError` со статусом 404.

Домен-пример — `tasks`: создать, список, карточка, частичное обновление, завершение.

## Стек

- Python 3.14
- Django 6.1
- django-ninja 1.7
- Pydantic v2
- PostgreSQL, psycopg 3
- uv, ruff, pytest

## Структура

```
src/config/             настройки Django, URL, сборка NinjaAPI
src/common/             TimeStampedModel, model_update, пагинация
src/core/               ApplicationError
src/tasks/              пример домена
  apis.py               эндпоинты
  schemas.py            SchemaIn / SchemaOut / FilterSchema
  exceptions.py         ошибки домена
  services.py           TaskService: get, list, create, update, complete
  models.py
  tests/
config.example.toml     образец конфигурации
config.toml             локальные значения, в git не попадает
```

Сервис домена — класс, метод — один use case: `TaskService.create`. Имена эндпоинтов: `<сущность>_<действие>_api`.

## Запуск

Нужны Python 3.14 и PostgreSQL.

```bash
uv sync --group dev
cp config.example.toml config.toml
```

В `config.toml` укажите доступ к PostgreSQL. Для базы из compose пользователь и пароль — `template_ninja`. Порт 5432 должен быть свободен:

```bash
docker compose up -d db
```

Дальше:

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

- API: http://127.0.0.1:8000/api/tasks
- Схема: http://127.0.0.1:8000/api/docs
- Проверка базы: http://127.0.0.1:8000/healthchecks/

`src/config/settings.py` читает только `config.toml` в корне проекта. Меняется окружение — меняется этот файл.

## Проверки

```bash
uv run ruff format .
uv run ruff check .
uv run pytest
```

## Новый сценарий

1. Поле или правило целостности — в модель и ограничение базы.
2. Вход и ответ — `SchemaIn` / `SchemaOut` в `schemas.py`.
3. Запись и правило — метод сервиса в `services.py`. Он принимает схему keyword-аргументом, вызывает `full_clean()` и сохраняет. Одиночное обновление идёт через `model_update`.
4. Эндпоинт в `apis.py` только вызывает метод сервиса и отдаёт схему.

Ошибка домена наследуется от `ApplicationError`. Для неё задаётся `status_code`, обработчик в `config/api.py` превращает её в JSON `{"message": "..."}`. Ошибка валидации входа остаётся 422 от Pydantic. `ValidationError` из `full_clean()` становится 400.

Чтение с фильтрами — `TaskService.list`. Карточка по id — `TaskService.get`.

В этот каркас сознательно не входят TaskIQ, pgtrigger и отдельный auth. Styleguide описывает их как следующие слои, когда появятся фоновые задачи и инварианты на уровне базы.
