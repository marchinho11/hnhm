fmt:
	@poetry run pre-commit run -a

test:
	@poetry run pytest -v --cov=hnhm --cov-report html --cov-report term tests/

lines:
	@poetry run pygount --format=summary --suffix=py hnhm/

lines-all:
	@poetry run pygount --format=summary --suffix=py hnhm/ tests/
