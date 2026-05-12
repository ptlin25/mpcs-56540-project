# Django-Poll-App

# Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.


## Setup virtual environment and install dependencies
```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```


## To migrate the database open terminal in project directory and type

```
python manage.py makemigrations
python manage.py migrate
```

## To use admin panel you need to create superuser using this command

```
python manage.py createsuperuser
```

## To Create some dummy text data for your app follow the step below:
```
pip install faker
python manage.py shell
import seeder
seeder.seed_all(30)
```
Here 30 is a number of entry. You can use it as your own

## To run the program in local server use the following command

```
python manage.py runserver
```

Then go to http://127.0.0.1:8000 in your browser

# Running Tests

## To run the Q3 unit tests use the following command

```
coverage run manage.py test polls accounts
```

## To generate the coverage report
```
coverage html
```
The coverage report is written to `htmlcov/index.html`