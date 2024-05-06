# Great Camp Hexpansion Quest

This is the main application for GCHQ.NET - Great Camp Hexpansion Quest

## Development

This project is based on [Django](https://www.djangoproject.com) and uses [Parcel](https://parceljs.org) to bundle frontend assets.

You will need [Python](https://www.python.org) 3.11 or later,  [Poetry](https://python-poetry.org) and [Node.JS](https://nodejs.org) 20 or [NVM](https://github.com/nvm-sh/nvm). You should also install GNU Make if it is not already available on your system.

### Setting up Frontend

Firstly, if you are using NVM, set the correct Node version: `nvm use 20` and then install the Node dependencies: `npm install`

The frontend assets can then be built using `npm run start` and will automatically update them as you change code.

### Setting up Backend

Firstly, install the Python dependencies using poetry: `poetry install`.

You can enter the virtualenv by running `poetry shell` or run commands using `poetry run <cmd>`.

You need a PostgreSQL database. This project **only** supports PostgreSQL.

You can run a copy of PostgreSQL for development by running `docker-compose up -d`

Once the database is connected, setup the tables by running: `./manage.py migrate`

A superuser can be created by running `./manage.py createsuperuser`

You can run the Django development server: `./manage.py runserver` or `make dev`


### Linting, Formatting and Tests

All automatic tests can be run by invoking Make: `make`

The following commands are also available:

- `make check` - run Django automated checks
- `make dev` - run Django's development server
- `make format` - format python code and templates
- `make format-check` - check that code is formatted correctly
- `make lint` - lint python code
- `make lint-fix` - lint python code and fix any errors where possible
- `make type` - run the type checker
- `make test` - run the Django unit test suite
- `make test-cov` - run the Django unit test suite and output a directory of test coverage info

## Production

When deploying to production, the [Django deployment guidelines](https://docs.djangoproject.com/en/5.0/howto/deployment/) should be followed.

Additionally, you will need to build the minified frontend assets for production: `npm run build` before running `./manage.py collectstatic`