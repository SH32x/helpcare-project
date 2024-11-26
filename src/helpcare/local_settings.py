from .settings import *

# Local settings, will not be pushed to GitHub
''' Locally run server:

python src/manage.py runserver --settings=helpcare.local_settings

Locally migrate:

python src/manage.py migrate --settings=helpcare.local_settings

'''


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}