FROM python:3.13-slim

# Set working directory
WORKDIR /app

COPY . .

COPY requirements.txt .

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off

# Install MongoDB client and required packages
RUN apt-get update && apt-get install -y \
    gnupg curl dirmngr \
    && curl -fsSL https://pgp.mongodb.com/server-7.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-7.0.gpg \
    --dearmor \
    && echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-7.0.gpg ] http://repo.mongodb.org/apt/debian bullseye/mongodb-org/7.0 main" | \
    tee /etc/apt/sources.list.d/mongodb-org-7.0.list \
    && apt-get update \
    && apt-get install -y mongodb-org-tools mongodb-mongosh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mongoimport --host='127.0.0.1' --db=cpppac --collection=sentenciados --type=csv --file=/app/28-02.csv --headerline

# Install dependencies

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install pymongo

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Run the application
# Replace "app.py" with your actual entry point
CMD ["python", "app.py"]

EXPOSE 80