FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pandas

COPY . .

CMD ["python", "airbnb_pipeline.py"]