FROM python:3.12-slim

WORKDIR /code
COPY requirements.txt alembic.ini ./
COPY alembic ./alembic
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY entrypoint.sh ./
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
