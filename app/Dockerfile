FROM python:3.12.2-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["sh", "-c", "streamlit run app.py --server.address $ADDRESS --server.port $PORT"]