test-all: test pre-commit

test:
	docker-compose -f docker-compose.test.yml build
	docker-compose -f docker-compose.test.yml run --rm limnoria-plugin-test supybot-test -v WeatherBot/


pre-commit:
	pre-commit run --all-files

black:
	black --line-length=79 ./

lint:
	flake8 ./

.PHONY: all
