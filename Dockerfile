FROM python:3.11.6-alpine3.18
WORKDIR /bot
COPY Pipfile.lock .
RUN pip install pipenv && pipenv sync
COPY . .
CMD pipenv run python src/main.py release
