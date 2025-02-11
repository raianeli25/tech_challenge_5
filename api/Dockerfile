FROM python:3.12.2-slim

WORKDIR /app

COPY . /app

# Instalar dependências do sistema necessárias para compilar pacotes como scikit-surprise
RUN apt-get update && apt-get install -y build-essential python3-dev gcc && apt-get install -y git && rm -rf /var/lib/apt/lists/*
 
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["sh", "-c", "uvicorn main:app --host $HOST --port $PORT --reload"]