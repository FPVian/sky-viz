Alembic docs:
> https://alembic.sqlalchemy.org/en/latest/index.html

Commands API:
> https://alembic.sqlalchemy.org/en/latest/api/commands.html

Alembic utils can be used to add autogenerate support for views in PostgreSQL:
> https://github.com/olirice/alembic_utils

Also consider unincluding views:
> https://alembic.sqlalchemy.org/en/latest/cookbook.html#don-t-emit-create-table-statements-for-views


## Manipulating databases:

- open the terminal and change directory to folder with alembic.ini file
- set environment variable to select correct database:

> `export SKYVIZ_ENV='dev'`

- check that the correct enviroment is set:

> `printenv SKYVIZ_ENV`

### Check for changes to the database model:

> `alembic check`

### Create a new revision:

> `alembic revision --autogenerate -m "<name of commit>"`

### Run migration/s:

> `alembic upgrade heads`

### Undo the last migration:

> `alembic downgrade -1`

### Restore database to its initial state:

> `alembic downgrade base`