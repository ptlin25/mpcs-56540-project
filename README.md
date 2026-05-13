# Django-Poll-App

# Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.


## Setup virtual environment and install dependencies
```
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
playwright install
```


## Migrate the database
```
python manage.py migrate
```

## To create dummy data for the performance tests, follow the steps below:
```
python manage.py shell
import seeder
seeder.seed_test()
```
This creates 
- user1, ..., user200  (password: password)
- 30 polls (IDs 1-30 on a fresh DB), 2 choices each
- Poll 30 is inactive so GET /polls/30/ renders the results page

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

## To run the Q4 performance tests
#### Run the program in one terminal
```
python manage.py runserver
```

#### Open another terminal with the virtual environment activated and run
```
# load test
LOCUST_TEST_PROFILE=load locust -f locustfile.py

# spike test
LOCUST_TEST_PROFILE=spike locust -f locustfile.py
```

## To run the Q5 tests
```
pytest tests/test_e2e.py -v
```

## To run the Q6 tests
```
pytest tests/test_integration.py -v
```