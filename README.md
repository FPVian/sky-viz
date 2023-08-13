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
- Run `bash ./scripts/setup.sh` to install dependencies on linux
- Run `python3 -m flights` and `python3 -m skyviz`

$~$

## Testing:
- Run `pytest`
- Add `ADSB_EXCHANGE_API_KEY_DEV` to Github repository secrets
- Tests are run automatically when opening a PR and merging to main

$~$

## Deployment (WIP):
- Build containers and push to Docker Hub
>- `docker build -t fpvian/sky-viz-flights:latest -f ./deployment/flights.Dockerfile .`
>- `docker build -t fpvian/sky-viz-skyviz:latest -f ./deployment/skyviz.Dockerfile .`
>- `docker push fpvian/sky-viz-flights:latest`
>- `docker push fpvian/sky-viz-skyviz:latest`

- Create Pulumi account and access token
- Create Azure account and service principal
- Populate ARM, PULUMI, & POSTGRES fields in .env file
- Install Pulumi 
>- `curl -fsSL https://get.pulumi.com | sh`

- Run Pulumi
>- `cd deployment/`
>- `export SKYVIZ_ENV='prod'`
>- `pulumi up`

- Update DNS records for domain
- Add webhooks to Docker Hub repositories
- New deployments are automatic on container push to docker hub

## Staging (WIP):
- Build containers and push to Docker Hub
- `export SKYVIZ_ENV='staging'`
- Run Pulumi in a separate stack
- [Staging Website](skyviz-staging.azurewebsites.net)
- Clean up resources with `pulumi destroy`

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
