<a name="readme-top"></a>

<!-- PROJECT LOGO -->
<div align="center">
  <a href="https://www.skyviz.app">
    <img src="src/skyviz/static/logo.png" alt="Logo" width="160" height="160">
  </a>

<h1 align="center">SkyViz</h1>

  <p align="center">
    Stores data streams from ADSB receivers to generate insights about the world above us.
  <p align="center">
    Note: This is a WIP, more visualizations soon to come!
    <br />
    <br />
    <a href="https://www.skyviz.app"><strong>skyviz.app »</strong></a>
    <br />
    <br />
    <a href="https://streamlit.io/"><img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" /></a>
    <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" /></a>
    <a href="https://www.pulumi.com/"><img src="https://img.shields.io/badge/Pulumi-8A3391?style=for-the-badge&logo=pulumi&logoColor=white" /></a>
    <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" /></a>
    <a href="https://azure.microsoft.com/"><img src="https://img.shields.io/badge/microsoft%20azure-0089D6?style=for-the-badge&logo=microsoft-azure&logoColor=white" /></a>
  </p>
</div>


<br />
<p align="center">
    <a href="https://www.linkedin.com/in/iangresov/"><img src="https://img.shields.io/badge/linkedin-0A66C2.svg?style=[style_name]&logo=linkedin&logoColor=white" /></a>
    <a href="mailto:ian@skyviz.app"><img src="https://img.shields.io/badge/gmail-EA4335.svg?style=[style_name]&logo=gmail&logoColor=white" /></a>
</p>
<br />


<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li>
      <a href="#development">Development</a>
      <ul>
        <li><a href="#testing">Testing</a></li>
      </ul>
    </li>
    <li>
      <a href="#deployment">Deployment</a>
      <ul>
        <li><a href="#staging">Staging</a></li>
      </ul>
    </li>
    <li><a href="#database-migrations">Database Migrations</a></li>
  </ol>
</details>


<!-- GETTING STARTED -->
## Getting Started
1. Create a free subsciption to [ADSBexchange](https://adsbexchange.com/) APIs on [RapidAPI](https://rapidapi.com)
2. Clone the repo
    ```sh
    git clone https://github.com/fpvian/sky-viz.git
    ```
3. Rename `.env.template` to `.env` and fill with api key
    ```
    ADSB_EXCHANGE_API_KEY_DEV=<your key here>
    ADSB_EXCHANGE_API_KEY_PROD=<your key here>
    ```
4. Install [Docker](https://docs.docker.com/get-docker/)
5. Start containers
    ```sh
    docker compose up
    ```
6. Navigate to [localhost:8501](localhost:8501)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

## Development:
1. Install [Python](https://www.python.org/downloads/)
2. Create and activate a virtual environment
    ```sh
    python3 -m venv .venv --upgrade-deps
    source .venv/bin/activate
    ```
3. Install packages and dependencies
    ```sh
    pip install --editable .
    ```
4. Run modules
    ```sh
    python3 -m flights &
    python3 -m skyviz
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

### Testing:
Tests are run automatically when opening a PR and merging to main. Just add `ADSB_EXCHANGE_API_KEY_DEV` to the Github repository secrets.
- Run all tests manually
    ```sh
    pytest
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

## Deployment:
Note that `webapp_name` in `src/flights/config/groups/general.py` and `server_name` in `src/flights/config/groups/db.py` *must be globally unique in Azure.*
1. Create [Pulumi account](https://www.pulumi.com/docs/get-started/) and [access token](https://www.pulumi.com/docs/pulumi-cloud/access-management/access-tokens/)
2. Create [Azure account](https://azure.microsoft.com/en-us/free/) and [service principal](https://www.pulumi.com/registry/packages/azure-native/installation-configuration/) with ["Contributer" role](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/service_principal_client_secret)
3. Create [Docker Hub account](https://hub.docker.com/) and [access token](https://docs.docker.com/docker-hub/access-tokens/)
4. Populate ARM, PULUMI, DOCKER, & POSTGRES fields in .env file
    ```
    ARM_CLIENT_ID=<your azure service principal client id>
    ARM_CLIENT_SECRET=<your azure service principal client secret>
    ARM_TENANT_ID=<from `az account list`>
    ARM_SUBSCRIPTION_ID=<id from `az account list`>
    PULUMI_ACCESS_TOKEN=<your pulumi token>
    DOCKER_USER=<your docker username>
    DOCKER_TOKEN=<your docker token>
    POSTGRES_PROD_ADMIN_USERNAME=<make up a username>
    POSTGRES_PROD_ADMIN_PASSWORD=<randomly generate a password>
    POSTGRES_PROD_USERNAME=<the same as admin username, until you manually create a user>
    POSTGRES_PROD_PASSWORD=<the same as admin password, until you manually create a user>
    POSTGRES_STAGING_ADMIN_USERNAME=<make up a username>
    POSTGRES_STAGING_ADMIN_PASSWORD=<randomly generate a password>
    POSTGRES_STAGING_USERNAME=<the same as staging admin username>
    POSTGRES_STAGING_PASSWORD=<the same as staging admin password>
    ```
5. Install Pulumi 
    ```sh
    curl -fsSL https://get.pulumi.com | sh
    ```
5. Run Pulumi
    ```sh
    cd deployment/
    export SKYVIZ_ENV='prod'
    export DOCKER_HOST='unix://'$HOME'/.docker/desktop/docker.sock'  # linux only
    pulumi up
    ```
6. Update DNS records and issue certificates for domain

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

### Staging:
1. Run Pulumi in a separate stack
    ```sh
    cd deployment/
    export SKYVIZ_ENV='staging'
    export DOCKER_HOST='unix://'$HOME'/.docker/desktop/docker.sock'  # linux only
    pulumi up
    ```
2. Navigate to [Staging Website](skyviz-staging.azurewebsites.net)
3. Clean up resources
    ```sh
    pulumi destroy
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

## Database Migrations:

1. Navigate to folder with alembic.ini file
    ```sh
    cd src/flights/db/
    ```
2. Set environment variable to select database
    ```sh
    export SKYVIZ_ENV='dev'  # postgres running in a local docker container
    ```
3. Check for changes to the database model
    ```sh
    alembic check
    ```
4. Create a new version
    ```sh
    alembic revision --autogenerate -m "<name of commit>"
    ```
5. Test migration (migrations are handled automatically)
    ```sh
    alembic upgrade heads
    ```
6. Undo the last migration
    ```sh
    alembic downgrade -1
    ```
7. Restore database to its initial state
    ```sh
    alembic downgrade base
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>