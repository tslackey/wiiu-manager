PYTHON ?= python3
.PHONY: test test-live doctor fetch

test:
	$(PYTHON) -m unittest discover -s tests -v

test-live:
	WIIU_LIVE_FETCH=1 $(PYTHON) -m unittest tests.test_live_fetch -v

doctor:
	./scripts/wiiu doctor

fetch:
	./scripts/wiiu fetch --profile recommended
	./scripts/wiiu stage
	./scripts/wiiu verify --profile recommended
