FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create required directories if they don't exist
RUN mkdir -p app/infrastructure
RUN mkdir -p app/services
RUN mkdir -p tests

CMD ["python", "main.py"] 