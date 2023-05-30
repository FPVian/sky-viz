'''
Rename this to secrets.py to store passwords and keys for different environments (required)
'''


class Default:

    class AdsbExchange:
        API_KEY: str = ''

    class Database:
        class Postgres:
            PASSWORD: str = ''


class Prod:
    pass


class Dev:
    pass
