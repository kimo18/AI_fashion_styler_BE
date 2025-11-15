# Use official Python slim image
FROM python:3.12.10-slim

# Set working directory
WORKDIR /AI_fashion_styler_BE

# Install dependencies
COPY requirements.txt .
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"]

