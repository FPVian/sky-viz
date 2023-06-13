# sky-viz
Monitors and stores data from adsb receivers to create visualiations and generate insights about the world above us.

Check it out! [skyviz.app](https://skyviz.app)

## Instructions
- create a subsciption to [ADSBexchange](https://adsbexchange.com/) APIs on [RapidAPI](https://rapidapi.com)
- rename `secrets.template.py` to `secrets.py` and fill in required values
- set environment variable if needed (defined in config/env.py)
- run setup.sh
- run `python3 -m flights` and `python3 -m skyviz`

#

### Open readme in the alembic folder for instructions on running database migrations

#

### Testing
- Run `pytest` in the project root to run all tests
