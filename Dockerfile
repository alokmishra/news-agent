FROM python:3.11-slim

WORKDIR /app

COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create the data directory
RUN mkdir -p /app/data

# Run the main script
CMD ["python", "src/main.py"]