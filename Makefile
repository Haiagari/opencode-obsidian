# Local-first knowledge workflow and security regression test targets.
.PHONY: test test-core test-extensions test-workflows test-wiki test-scripts test-retrieve test-yaml test-unit test-all help

help:
	@echo "Knowledge workflow test targets:"
	@echo "  make test-core       Core checks; no Docker or n8n configuration required"
	@echo "  make test-extensions Optional n8n workflow/config validation"
	@echo "  make test            Core plus extension checks"
	@echo "  make test-unit       Python unit and local lifecycle tests"
	@echo "  make test-retrieve   BM25 retrieval checks"

test: test-core test-extensions
	@echo ""
	@echo "🎉 Core and extension suites passed"

test-core: test-yaml test-wiki test-scripts test-retrieve test-unit

test-extensions: test-workflows test-yaml-extensions

test-workflows:
	@echo "========================================"
	@echo "  Suite: Optional n8n Workflow Connections"
	@echo "========================================"
	@python3 tests/test_workflow_connections.py
	@echo ""

test-wiki:
	@echo "========================================"
	@echo "  Suite: Wiki Integrity"
	@echo "========================================"
	@bash tests/test_wiki_integrity.sh
	@echo ""

test-scripts:
	@echo "========================================"
	@echo "  Suite: Scripts Validation"
	@echo "========================================"
	@bash tests/test_scripts.sh
	@echo ""

test-yaml:
	@python3 -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml')); print('  ✅ CI YAML valid')"

test-yaml-extensions:
	@python3 -c "import yaml; yaml.safe_load(open('extensions/n8n/docker-compose.yml')); print('  ✅ n8n compose YAML valid')"

test-retrieve:
	@echo "========================================"
	@echo "  Suite: BM25 Retrieval"
	@echo "========================================"
	@python3 scripts/retrieve.py status > /dev/null 2>&1 || python3 scripts/bm25-index.py build
	@python3 scripts/retrieve.py status > /dev/null 2>&1 && echo "  ✅ Índice BM25 existe" || (echo "  ❌ Índice BM25 no encontrado" && exit 1)
	@python3 scripts/retrieve.py "test query búsqueda" --top 2 > /dev/null 2>&1 && echo "  ✅ Búsqueda BM25 funciona" || (echo "  ❌ Búsqueda BM25 falló" && exit 1)

test-unit:
	@echo "========================================"
	@echo "  Suite: Unit Tests (FTS5, Lock, Sanitize)"
	@echo "========================================"
	@python3 -m unittest discover -s tests -p "test_*.py"

test-all: test
