FROM python:3.11
WORKDIR /bot
COPY . /bot
RUN pip install pipenv && pipenv install --deploy --ignore-pipfile
CMD python src/main.py release
