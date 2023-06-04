# %%
from flights.config.settings import s

import alembic.config

import sqlite3
import os


os.chdir(f'{s.project_root}/src/flights/db/')

# %%
alembic.config.main(argv=['upgrade', 'heads'])

# %%
con = sqlite3.connect(s.db.sqlite_path)

# %%
os.remove(s.db.sqlite_path)

# %%
