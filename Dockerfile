FROM python:3.11
WORKDIR /bot
COPY Pipfile .
RUN pip install pipenv && pipenv install --deploy
COPY . .
CMD pipenv run python src/main.py release
