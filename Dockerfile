FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    APP_ENV=production \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install -r ./requirements.txt

COPY src ./src
COPY public ./public
COPY monopoly_board.json ./

EXPOSE 8080

CMD ["python", "-m", "src.main", "./monopoly_board.json"]
