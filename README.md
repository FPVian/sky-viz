# SkyViz

### Stores data streams from adsb receivers to create visualiations and generate insights about the world above us.

$~$

## Check it out ----> [skyviz.app](https://www.skyviz.app)

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

## Deployment:
- Create Pulumi account and access token
- Create Azure account and service principal
- Create Docker Hub account and access token
- Populate ARM, PULUMI, DOCKER, & POSTGRES fields in .env file
- Install Pulumi 
>- `curl -fsSL https://get.pulumi.com | sh`

- Run Pulumi (omit container app alerts on first prod run)
>- `cd deployment/`
>- `export SKYVIZ_ENV='prod'`
>- `export DOCKER_HOST='unix:///home/ian/.docker/desktop/docker.sock'`
>- `pulumi up`

- Update DNS records and issue certificates for domain
- New deployments are automatic on running pulumi up

$~$

## Staging:
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
