FROM python:3.11.3-alpine3.17

ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$PATH:$VIRTUAL_ENV/bin"
ENV PYTHONUNBUFFERED=1

RUN python3 -m venv "$VIRTUAL_ENV" && pip3 install --no-cache-dir --upgrade pip==23.1.1

COPY requirements.txt /tmp
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
ENV PYTHONPATH="$PYTHONPATH:/app"
COPY . /app

CMD ["python3", "web.py"]
EXPOSE 9000
