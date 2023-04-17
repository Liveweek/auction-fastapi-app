FROM python:3.10-slim

# Настраиваем переменную окружения PYTHONUNBUFFERED, чтобы скрипты Python работали корректно в контейнере
ENV PYTHONUNBUFFERED 1

# Копируем файлы проекта в контейнер
WORKDIR /app
COPY pyproject.toml /app
COPY start_worker.sh /app
RUN chmod +x start_worker.sh


COPY /auction_project /app/auction_project

ENV PYTHONPATH=${PYTHONPATH}:${PWD} 

RUN pip3 install poetry

# Устанавливаем зависимости через poetry
RUN poetry config virtualenvs.create false
RUN cd auction_project
RUN poetry install --no-interaction --no-ansi

# Запускаем приложение
WORKDIR /app/auction_project
CMD mkdir -p static static/auctions static/vendor static/categories && /bin/bash /app/start_worker.sh && poetry run run-api