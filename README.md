# SkyViz

### Stores data streams from adsb receivers to create visualiations and generate insights about the world above us.

$~$

## Check it out ----> [skyviz.app](https://skyviz.app)

$~$

# Instructions
- Create a subsciption to [ADSBexchange](https://adsbexchange.com/) APIs on [RapidAPI](https://rapidapi.com)
- Rename `.env.template` to `.env` and fill with api key
- Install Docker
- Run `docker compose up`
- Navigate to [localhost:8501](localhost:8501)

$~$

## Development:
- Run setup.sh to install dependencies on linux
- Run `python3 -m flights` and `python3 -m skyviz`

$~$

## Testing:
- Run `pytest`
- Tests are run automatically when opening a PR and merging to main

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

Test migration (migrations are handled automatically):
> `alembic upgrade heads`

Undo the last migration:
> `alembic downgrade -1`

Restore database to its initial state:
> `alembic downgrade base`
