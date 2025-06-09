FROM python:3.10-slim
WORKDIR /app
COPY ../../.. /app
RUN pip install --no-cache-dir poetry && poetry install --no-dev
CMD ["python", "-m", "agents.sample_oracle.src.cli", "run"]
