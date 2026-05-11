import os
from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examsite.settings')

app = get_wsgi_application()
call_command('migrate', interactive=False)
