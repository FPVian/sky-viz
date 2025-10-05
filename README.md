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

<p align="center">
    <a href="https://htmlpreview.github.io/?https://github.com/FPVian/sky-viz/blob/python-coverage-comment-action-data/htmlcov/index.html"><img src="https://raw.githubusercontent.com/FPVian/sky-viz/python-coverage-comment-action-data/badge.svg" /></a>
</p>

<!-- <br /> -->
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
      <a href="#project-overview">Project Overview</a>
      <ul>
        <li><a href="#data-model">Data Model</a></li>
      </ul>
    </li>
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


<!-- PROJECT OVERVIEW -->
## Project Overview

The ADS-B Exchange network collects telemetry from plane transponders and publishes the current state of the airspace through their APIs. This project stores and transforms the data to make it available for historical analysis in a Streamlit web app.

Resources are containerized using Docker and hosted in Azure. CI/CD is enabled through Pulumi and Github Actions. Database versioning and migrations are handled by SQLAlchemy ORM and Alembic. Environment configuration is managed using Hydra.

$~$

<div align="center">
  <img src="src/skyviz/static/architecture_diagram.png" alt="Architecture Diagram">
</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

### Data Model
<div align="center">
  <img src="src/skyviz/static/db_model_diagram.svg" alt="Data Model Diagram">
</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

<!-- GETTING STARTED -->
## Getting Started
1. Create a free subsciption to [ADSBexchange](https://adsbexchange.com/) APIs on [RapidAPI](https://rapidapi.com)
1. Clone the repo
    ```sh
    git clone https://github.com/fpvian/sky-viz.git
    ```
1. Rename `.env.template` to `.env` and fill with api key
    ```
    ADSB_EXCHANGE_API_KEY_DEV=<your key here>
    ```
1. Install [Docker](https://docs.docker.com/get-docker/)
1. Start containers
    ```sh
    docker compose up
    ```
1. Navigate to [localhost:8501](localhost:8501)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

<!-- DEVELOPMENT -->
## Development:
1. Install [Python](https://www.python.org/downloads/)
1. Create and activate a virtual environment
    ```sh
    python3 -m venv .venv --upgrade-deps
    source .venv/bin/activate
    ```
1. Install packages and dependencies
    ```sh
    pip install --editable .
    ```
1. Run modules
    ```sh
    python3 -m flights &
    python3 -m transform &
    streamlit run ./src/skyviz/Home.py
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

<!-- TESTING -->
### Testing: 
Tests are run automatically when opening a PR and merging to main. Coverage reports are added to the PR as a comment.
1. Add `ADSB_EXCHANGE_API_KEY_DEV` to the Github repository secrets
1. Run all tests and generate coverage report
    ```sh
    pytest
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

<!-- DEPLOYMENT -->
## Deployment:
After following these steps, deployments will be handled automatically when merging to main. Note that `webapp_name` in `src/flights/config/groups/general.py` and `server_name` in `src/flights/config/groups/db.py` *must be globally unique in Azure.*
1. Create [Pulumi account](https://www.pulumi.com/docs/get-started/) and [access token](https://www.pulumi.com/docs/pulumi-cloud/access-management/access-tokens/)
1. Create [Azure account](https://azure.microsoft.com/en-us/free/) and [service principal](https://www.pulumi.com/registry/packages/azure-native/installation-configuration/) with ["Contributer" role](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/service_principal_client_secret)
1. Create [Docker Hub account](https://hub.docker.com/) and [access token](https://docs.docker.com/docker-hub/access-tokens/)
1. Populate ARM, PULUMI, DOCKER, POSTGRES, and ADSB fields in .env file **and GitHub repository secrets**
    ```
    ARM_CLIENT_ID=<your azure service principal client id>
    ARM_CLIENT_SECRET=<your azure service principal client secret>
    ARM_TENANT_ID=<from `az account list`>
    ARM_SUBSCRIPTION_ID=<id from `az account list`>
    PULUMI_ACCESS_TOKEN=<your pulumi token>
    DOCKER_USER=<your docker username>
    DOCKER_TOKEN=<your docker token>
    POSTGRES_USERNAME=<make up a username>
    POSTGRES_PASSWORD=<randomly generate a password>
    ADSB_EXCHANGE_API_KEY_DEV=<your key here>
    ADSB_EXCHANGE_API_KEY_PROD=<your key here>
    ```
1. Install Pulumi
    ```sh
    curl -fsSL https://get.pulumi.com | sh
    ```
1. Run Pulumi
    ```sh
    cd deployment/
    export SKYVIZ_ENV=prod
    pulumi up
    ```
1. Update DNS records and issue certificates for domain
1. Install Pulumi app in GitHub repository to preview changes to prod resources as a PR comment

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

<!-- STAGING -->
### Staging:
Staging environment is automatically deployed when opening a pull request to main and automatically destroyed when merged. Follow these steps to manually manage staging environment.
1. Run Pulumi in a separate stack
    ```sh
    cd deployment/
    export SKYVIZ_ENV=staging
    pulumi up
    ```
1. Navigate to [Staging Website](https://skyviz-staging.azurewebsites.net)
1. Clean up resources
    ```sh
    pulumi destroy
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

$~$

<!-- DATABASE MIGRATIONS -->
## Database Migrations:

1. Navigate to folder with alembic.ini file
    ```sh
    cd src/database/
    ```
1. Set environment variable to select database
    ```sh
    export SKYVIZ_ENV=test  # ephemeral sqlite database
    ```
1. Check for changes to the database model
    ```sh
    alembic check
    ```
1. Create a new version
    ```sh
    alembic revision --autogenerate -m "<name of commit>"
    ```
1. Test migration (migrations are handled automatically)
    ```sh
    alembic upgrade heads
    ```
1. Undo the last migration
    ```sh
    alembic downgrade -1
    ```
1. Restore database to its initial state
    ```sh
    alembic downgrade base
    ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>