FROM python:3.11
WORKDIR /bot
COPY . /bot
RUN pip install pipenv && pipenv install --deploy
CMD pipenv run python src/main.py release
