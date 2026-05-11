"""
Vercel serverless entry point.
This file must live at api/index.py in your project root.
"""
import os
import django
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'examsite.settings')
django.setup()

app = get_wsgi_application()
