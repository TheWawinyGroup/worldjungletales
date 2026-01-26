
## A nature and wildlife blog

## Application Setup

The assumption here is that you are using a **Linux** PC

Ensure PostgreSQL is installed in your computer, if not follow this [Instructions](https://documentation.ubuntu.com/server/how-to/databases/install-postgresql/index.html)

Make sure python3.13 is installed in your PC

create a Virtual environment on this repo directory using

    python3.13 -m venv venv

Activate the virtual environment
    source venv/bin/activate

Install application dependencies using

    pip install -r requirements.txt


## Install the git hook scripts for pre-commit

    pre-commit install
    pre-commit install --hook-type commit-msg

## Setting up the Database

The project runs on Postgresql as the database server.
To set this up open postgres by running:

    sudo -u postgres psql

If you do not have postgres set up follow this [postgresql](https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart) tutorial to learn.

You will need the following in your postgres database instance:

1. A super user `worldjungletales_user` with password `worldjungletales_pass` .
2. A database `worldjungletales`.

After Postgres is open (as `postgres=#`) run the setup [script](https://github.com/limit-group/worldjungletales/blob/master/setup.sql) found at the root repository directory.


## Making Migrations

while in the worldjungletales directory, activate the virtual environment through:`. venv/bin/activate`

To apply the database migrations in the worldjungletales project run:

    ./manage.py migrate


## Start app locally
Create a env.sh file and copy contents of the `.env.sh.example` file into it.

Source the environmental variable by running the below

    source env.sh

Start the app in dev mode

    python3.12 manage.py runserver 8001



&copy; LimitGroup 2024
