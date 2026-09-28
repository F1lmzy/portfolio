PY ?= python3
PORT ?= 8000

.PHONY: build themes test check serve clean

build: themes
	$(PY) build.py

themes:
	$(PY) tools/build_themes.py

check:
	$(PY) -m py_compile build.py render.py content.py tools/build_themes.py tests/test_site.py
	@echo "compile ok"

test: build check
	$(PY) tests/test_site.py

serve: build
	@echo "serving on http://127.0.0.1:$(PORT)/"
	cd docs && $(PY) -m http.server $(PORT) --bind 127.0.0.1

clean:
	rm -rf docs __pycache__ tools/__pycache__ tests/__pycache__ static/themes.css static/themes.json
