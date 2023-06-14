# SkyViz

### Stores data streams from adsb receivers to create visualiations and generate insights about the world above us.

$~$

## Check it out ----> [skyviz.app](https://skyviz.app)

$~$

# Instructions
- create a subsciption to [ADSBexchange](https://adsbexchange.com/) APIs on [RapidAPI](https://rapidapi.com)
- rename `secrets.template.py` to `secrets.py` and fill in required values
- set environment variable if needed (defined in config/env.py)
- run setup.sh
- run `python3 -m flights` and `python3 -m skyviz`

$~$

## Manipulating databases:

Open the terminal and navigate to folder with alembic.ini file
> `cd src/flights/db/`

Set environment variable to select correct database. For a local postgres docker container:
> `export SKYVIZ_ENV='dev'`

Check that the enviroment variable is set:
> `printenv SKYVIZ_ENV`

Check for changes to the database model:
> `alembic check`

Create a new revision:
> `alembic revision --autogenerate -m "<name of commit>"`

Run migration:
> `alembic upgrade heads`

Undo the last migration:
> `alembic downgrade -1`

Restore database to its initial state:
> `alembic downgrade base`

$~$

## Testing:
Open terminal in project root and run all tests:
> `pytest`
