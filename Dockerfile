FROM python:3.10-slim

WORKDIR /app

# Install PostgreSQL dev libraries
RUN apt-get update && apt-get install -y libpq-dev gcc

# Copy and install dependencies
COPY requirement.txt .
RUN pip install --upgrade pip && pip install -r requirement.txt

# Copy app
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

