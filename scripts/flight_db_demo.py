# %%
from flights.config.settings import s

import alembic.config

import sqlite3
import os

os.chdir(f'{s.BASE_DIR}/db/')

# %%
alembic.config.main(argv=['upgrade', 'heads'])

# %%
con = sqlite3.connect(s.Database.SQLITE_PATH)

# %%
os.remove(s.Database.SQLITE_PATH)

# %%
