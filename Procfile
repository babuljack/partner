web: daphne -b 0.0.0.0 -p $PORT Social.asgi:application -v2
worker: python manage.py runworker channels --settings=Social.settings -v2