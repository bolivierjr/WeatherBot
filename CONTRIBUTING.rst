How to Contribute
=================

Always happy to get issues identified and pull requests!

Getting your pull request merged in
------------------------------------

#. Keep it small. The smaller the pull request the more likely I'll pull it in.
#. Pull requests that fix a current issue get priority for review.
#. Make sure you add tests to your fix or feature pull requests if none are available.

Installation
------------

Fork the repo and change into your Limnoria plugins/ directory or any direcotry you choose to clone this
repo and run commands:

    $ git clone https://github.com/<YourUserNameHere>/WeatherBot.git

Checkout to a feature/fix branch to make changes.

    $ cd WeatherBot/

    $ cp .env.example.test .env.test && cp .env.example .env

    $ pip install -r requirements/requirements-test.txt

Remember to fill out your .env file with valid API keys.

Please install docker and docker-compose to run the tests.

Must be running at least python 3.6 or higher.

Testing
-------

Run the Tests
~~~~~~~~~~~~~

Once docker and docker-compose is installed, you can run:

    $ make test

or

    $ make test-all

Alternatively, you can use the supybot-test command directly, but you have a chance of removing
your database if you're not in a seperate venv and using requirements.test.txt. You can run:

    $ supybot-test WeatherBot/

Also, look in the Makefile for make commands about linting and formatting.
Happy Contributing! :)
