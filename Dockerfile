FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirement.txt .
RUN pip install --upgrade pip && pip install -r requirement.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
