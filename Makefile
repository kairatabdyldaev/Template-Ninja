.DEFAULT_GOAL := help

help: ## Показать список команд
	@echo "Please use \`make <target>' where <target> is one of"
	@grep '^[a-zA-Z]' ${MAKEFILE_LIST} | sort | awk -F ':.*?## ' 'NF==2 {printf "\033[36m  %-25s\033[0m %s\n", $$1, $$2}'

all: format static test ## Отформатировать код и прогнать проверки

format: ## Отформатировать код
	uv run ruff format .
	uv run ruff check . --fix

format_check: ## Проверить форматирование без правок
	uv run ruff format --check .
	uv run ruff check .

static: ## Статический анализ
	uv run ruff check .

test: ## Запустить тесты
	uv run pytest

install: ## Установить зависимости
	uv sync --group dev

.PHONY: *
