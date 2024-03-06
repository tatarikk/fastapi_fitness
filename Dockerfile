FROM python:3.9

RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

COPY . .

WORKDIR /src

RUN ls

COPY requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
