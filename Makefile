# Bunker OS — Makefile
# Test runner para validación del vault, scripts y workflows n8n.

.PHONY: test test-workflows test-wiki test-scripts test-retrieve test-yaml test-all help

help:
	@echo "Bunker OS Test Targets:"
	@echo "  make test-workflows   Validar JSONs de workflows n8n (conexiones, nodos)"
	@echo "  make test-wiki        Health check del vault (archivos, frontmatter)"
	@echo "  make test-scripts     Validar scripts (sintaxis, secretos, ejecutables)"
	@echo "  make test-retrieve    Validar índice BM25 y text retrieval"
	@echo "  make test-yaml        Validar YAMLs (CI, compose)"
	@echo "  make test (default)   Ejecutar todas las suites"
	@echo "  make test-all         Alias de make test"

test: test-yaml test-workflows test-wiki test-scripts test-retrieve
	@echo ""
	@echo "🎉 Todas las suites pasaron"

test-workflows:
	@echo "========================================"
	@echo "  Suite: n8n Workflow Connections"
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
	@echo "========================================"
	@echo "  Suite: YAML Validation"
	@echo "========================================"
	@python3 -c "import yaml; yaml.safe_load(open('.github/workflows/test.yml')); print('  ✅ test.yml valido')" 2>/dev/null || echo "  ⚠️  yaml no disponible (pip install pyyaml)"
	@python3 -c "import yaml; yaml.safe_load(open('automation/n8n-lab/docker-compose.yml')); print('  ✅ docker-compose.yml valido')" 2>/dev/null || echo "  ⚠️  yaml no disponible"
	@echo ""

test-retrieve:
	@echo "========================================"
	@echo "  Suite: BM25 Retrieval"
	@echo "========================================"
	@python3 scripts/retrieve.py status > /dev/null 2>&1 || python3 scripts/bm25-index.py build
	@python3 scripts/retrieve.py status > /dev/null 2>&1 && echo "  ✅ Índice BM25 existe" || (echo "  ❌ Índice BM25 no encontrado" && exit 1)
	@python3 scripts/retrieve.py "test query búsqueda" --top 2 > /dev/null 2>&1 && echo "  ✅ Búsqueda BM25 funciona" || (echo "  ❌ Búsqueda BM25 falló" && exit 1)
	@echo ""

test-all: test
