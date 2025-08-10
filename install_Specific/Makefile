# Required variables
ifeq ($(OS),Windows_NT)
	PYTHON := python
	PY := .venv/Scripts/python
	PIP := .venv/Scripts/pip
	FLAKE8 := .venv/Scripts/flake8
else
	PYTHON := python3
	PY := .venv/bin/python
	PIP := .venv/bin/pip
	FLAKE8 := .venv/bin/flake8
endif

YARN := yarn --cwd lncrawl-web
VERSION := $(shell $(PYTHON) -c "print(open('lncrawl/VERSION').read().strip())")

# --- NOUVELLES VARIABLES POUR LA DÉTECTION DE VERSION PYTHON ---
# Détection de la version majeure.mineure de Python utilisée par le système
PYTHON_MAJOR_MINOR := $(shell $(PYTHON) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
# Détection de la version complète de Python (majeure.mineure.patch)
PYTHON_FULL_VERSION := $(shell $(PYTHON) -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
# Convertir la version en un seul entier pour des comparaisons plus fines (si nécessaire)
PYTHON_VERSION_INT := $(shell $(PYTHON) -c "import sys; print((sys.version_info.major * 100000) + (sys.version_info.minor * 1000) + sys.version_info.micro)")

# Default target (help/info)
.PHONY: clean version build_docker help install-py-by-version # Ajout des nouvelles cibles PHONY
_: version

# Affiche la commande pour activer l'environnement virtuel
activate-venv:
	ifeq ($(OS),Windows_NT)
		@echo "Pour activer l'environnement virtuel, exécutez :"
		@echo "  .venv\\Scripts\\activate.bat"
		@echo "Ou pour PowerShell :"
		@echo "  .venv\\Scripts\\Activate.ps1"
	else
		@echo "Pour activer l'environnement virtuel, exécutez :"
		@echo "  source .venv/bin/activate"
	endif

version:
	@echo Current version: $(VERSION)

# Clean target
clean:
ifeq ($(OS),Windows_NT)
	@powershell -Command "try { Remove-Item -ErrorAction SilentlyContinue -Recurse -Force .venv, logs, build, dist } catch {}; exit 0"
	@powershell -Command "Get-ChildItem -ErrorAction SilentlyContinue -Recurse -Directory -Filter '*.egg-info' | Remove-Item -Recurse -Force"
	@powershell -Command "Get-ChildItem -ErrorAction SilentlyContinue -Recurse -Directory -Filter '__pycache__' | Remove-Item -Recurse -Force"
	@powershell -Command "Get-ChildItem -ErrorAction SilentlyContinue -Recurse -Directory -Filter 'node_modules' | Remove-Item -Recurse -Force"
else
	[cite_start]@rm -rf .venv logs build dist [cite: 1]
	@find . -name '*.egg-info' -type d -exec rm -rf '{}' \;
	@find . -name '__pycache__' -type d -exec rm -rf '{}' \;
	@find . -name 'node_modules' -type d -exec rm -rf '{}' \;
endif

# Setup virtual environment in .venv
setup:
	[cite_start]$(PYTHON) -m venv .venv [cite: 1]
	[cite_start]$(PY) -m pip install -q -U pip [cite: 1]

# Nouvelle cible pour installer les dépendances Python en fonction de la version
install-py-by-version: setup
	@echo "Installation des dépendances Python via script conditionnel..."
	$(PY) install_pip.py # Exécute le script Python avec l'interpréteur du venv

# Install node modules in lncrawl-web
install-web:
	[cite_start]$(YARN) install [cite: 1]

# La cible 'install' appellera maintenant la nouvelle cible conditionnelle
install: install-py-by-version install-web

# Build wheel package and executable
build-web:
	[cite_start]$(YARN) build [cite: 1]

build-wheel:
	[cite_start]$(PY) -m build -w [cite: 1]

build-exe:
	[cite_start]$(PY) setup_pyi.py [cite: 1]

build: version install build-web build-wheel build-exe

# Lint project files
start-server:
	[cite_start]$(PY) -m lncrawl -b server -ll [cite: 1]

start-web:
	[cite_start]$(YARN) dev [cite: 1]

# Lint project files
lint-py:
	[cite_start]$(FLAKE8) --config .flake8 -v --count --show-source --statistics [cite: 1]

lint-web:
	[cite_start]$(YARN) lint [cite: 1]

lint: lint-py lint-web

# Push tag
pull:
	[cite_start]git pull --rebase --autostash [cite: 1]

remove-tag:
	[cite_start]git push --delete origin "v$(VERSION)" [cite: 1]
	[cite_start]git tag -d "v$(VERSION)" [cite: 1]

push-tag: pull
	[cite_start]git tag "v$(VERSION)" [cite: 1]
	[cite_start]git push --tags [cite: 1]

push-tag-force: pull
	[cite_start]git push --delete origin "v$(VERSION)" [cite: 1]
	[cite_start]git tag -d "v$(VERSION)" [cite: 1]
	[cite_start]git tag "v$(VERSION)" [cite: 1]
	[cite_start]git push --tags [cite: 1]

# --- CIBLE POUR LA CONSTRUCTION DOCKER CONDITIONNELLE ---
build_docker:
    @echo "--- Starting conditional Docker build via Python script ---"
    $(PY) install_docker.py # Exécute le script Python pour la construction Docker
    @echo "--- Conditional Docker build finished ---"

help:
	@echo "Utilisation des cibles Make:"
	@echo "  make                            - Affiche la version actuelle."
	@echo "  make setup                      - Crée et initialise l'environnement virtuel."
	@echo "  make install-py-by-version      - Installe les dépendances Python dans l'environnement virtuel en fonction de la version de Python."
	@echo "  make install-web                - Installe les modules Node.js pour le web."
	@echo "  make install                    - Exécute install-py-by-version et install-web."
	@echo "  make build-web                  - Construit les assets web."
	@echo "  make build-wheel                - Construit le paquet wheel Python."
	@echo "  make build-exe                  - Construit l'exécutable."
	@echo "  make build                      - Exécute version, install, build-web, build-wheel, build-exe."
	@echo "  make build_docker               - Construit l'image Docker appropriée en fonction de la version de Python système."
	@echo "  make start-server               - Démarre le serveur Python."
	@echo "  make start-web                  - Démarre le serveur de développement web."
	@echo "  make lint-py                    - Lance le linting Python."
	@echo "  make lint-web                   - Lance le linting web."
	@echo "  make lint                       - Exécute lint-py et lint-web."
	@echo "  make pull                       - Tire les dernières modifications du dépôt Git."
	@echo "  make remove-tag                 - Supprime le tag Git de la version courante."
	@echo "  make push-tag                   - Pousse le tag Git de la version courante."
	@echo "  make push-tag-force             - Force la suppression et le push du tag Git."
	@echo "  make clean                      - Nettoie les fichiers de build et caches."
	@echo "  make help                       - Affiche cette aide."