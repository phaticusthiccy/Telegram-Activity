@echo off

REM Byte-compiled / optimized / DLL files
rmdir /s /q __pycache__
del /q *.py[cod]
del /q *$py.class

REM C extensions
del /q *.so

REM Distribution / packaging
del /q .Python
rmdir /s /q build/
rmdir /s /q develop-eggs/
rmdir /s /q dist/
rmdir /s /q downloads/
rmdir /s /q eggs/
rmdir /s /q .eggs/
rmdir /s /q lib/
rmdir /s /q lib64/
rmdir /s /q parts/
rmdir /s /q sdist/
rmdir /s /q var/
rmdir /s /q wheels/
rmdir /s /q pip-wheel-metadata/
rmdir /s /q share/python-wheels/
del /q *.egg-info/
del /q .installed.cfg
del /q *.egg
del /q MANIFEST

REM PyInstaller
del /q *.manifest
del /q *.spec

REM Installer logs
del /q pip-log.txt
del /q pip-delete-this-directory.txt

REM Unit test / coverage reports
rmdir /s /q htmlcov/
rmdir /s /q .tox/
rmdir /s /q .nox/
del /q .coverage
del /q .coverage.*
del /q .cache
del /q nosetests.xml
del /q coverage.xml
del /q *.cover
del /q *.py,cover
rmdir /s /q .hypothesis/
rmdir /s /q .pytest_cache/

REM Translations
del /q *.mo
del /q *.pot

REM Django stuff
del /q *.log
del /q local_settings.py
del /q db.sqlite3
del /q db.sqlite3-journal

REM Flask stuff
rmdir /s /q instance/
rmdir /s /q .webassets-cache

REM Scrapy stuff
rmdir /s /q .scrapy

REM Sphinx documentation
rmdir /s /q docs/_build/

REM PyBuilder
rmdir /s /q target/

REM Jupyter Notebook
rmdir /s /q .ipynb_checkpoints

REM IPython
rmdir /s /q profile_default/
del /q ipython_config.py

REM pyenv
del /q .python-version

REM pipenv
del /q .Pipfile.lock

REM PEP 582
rmdir /s /q __pypackages__/

REM Celery stuff
del /q celerybeat-schedule
del /q celerybeat.pid

REM SageMath parsed files
del /q *.sage.py

REM Environments
del /q .env
del /q .venv
rmdir /s /q env/
rmdir /s /q venv/
rmdir /s /q ENV/
rmdir /s /q env.bak/
rmdir /s /q venv.bak/

REM Spyder project settings
del /q .spyderproject
del /q .spyproject

REM Rope project settings
del /q .ropeproject

REM mkdocs documentation
rmdir /s /q site/

REM mypy
rmdir /s /q .mypy_cache/
del /q .dmypy.json
del /q dmypy.json

REM Pyre type checker
rmdir /s /q .pyre/

REM Custom
del /q *.session
del /q *.session-journal

echo.
pause
