FROM python:3.12-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project

COPY . .

RUN uv run playwright install --with-deps

EXPOSE 9000

CMD ["uv", "run", "python", "main.py"]