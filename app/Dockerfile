FROM python:3.12.2-slim

WORKDIR /app

COPY . /app

# COPY ./app/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["streamlit", "run", "app.py"]
