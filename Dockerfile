FROM python:3.10-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ './sortgs.py' ]
