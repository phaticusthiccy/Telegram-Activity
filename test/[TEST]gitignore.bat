@echo off
rmdir /s /q __pycache__
del /q *.py[cod]
del /q *$py.class
del /q *.so
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
del /q *.manifest
del /q *.spec
del /q pip-log.txt
del /q pip-delete-this-directory.txt
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
del /q *.mo
del /q *.pot
del /q *.log
del /q local_settings.py
del /q db.sqlite3
del /q db.sqlite3-journal
rmdir /s /q instance/
rmdir /s /q .webassets-cache
rmdir /s /q .scrapy
rmdir /s /q docs/_build/
rmdir /s /q target/
rmdir /s /q .ipynb_checkpoints
rmdir /s /q profile_default/
del /q ipython_config.py
del /q .python-version
del /q .Pipfile.lock
rmdir /s /q __pypackages__/
del /q celerybeat-schedule
del /q celerybeat.pid
del /q *.sage.py
del /q .env
del /q .venv
rmdir /s /q env/
rmdir /s /q venv/
rmdir /s /q ENV/
rmdir /s /q env.bak/
rmdir /s /q venv.bak/
del /q .spyderproject
del /q .spyproject
del /q .ropeproject
rmdir /s /q site/
rmdir /s /q .mypy_cache/
del /q .dmypy.json
del /q dmypy.json
rmdir /s /q .pyre/
del /q *.session
del /q *.session-journal
echo.
pause
