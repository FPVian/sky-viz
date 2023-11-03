import os

'''
Since alembic generates it's own config based on the environment,
the environment is set to 'test' for ephemeral db testing.
'''


os.environ['SKYVIZ_ENV'] = 'test'
