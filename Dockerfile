FROM python:3.11
COPY Pipefile.lock /bot
RUN pip install pipenv && pipenv install --deploy
WORKDIR /bot
COPY . /bot
CMD pipenv run python src/main.py release
