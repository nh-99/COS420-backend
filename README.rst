COS420-backend
==============================

Implements a backend that stores & tracks employee time and generates reports at the end of the pay cycle

.. image:: https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg
     :target: https://github.com/pydanny/cookiecutter-django/
     :alt: Built with Cookiecutter Django



Deployment
----------
Local
^^^^^

To deploy the app locally (for testing/development), you will need to:
#. Create a virtualenv (basic).
#. Install application package as develop.
   .. code-block:: bash
        python setup.py develop
#. Serve the application itself:
   .. code-block:: bash
        export FALCON_SETTINGS_MODULE=cos420_backend.settings.local
        gunicorn cos420_backend.app:app --bind:127.0.0.1:8000 --reload

   Or
   
   .. code-block:: bash
        export FALCON_SETTINGS_MODULE=cos420_backend.settings.local
        python cos420_backend/app.py

It is very important to set the environment before serving the app or it won't work.



Docker
^^^^^^

To tun docker container application you just need to run:

