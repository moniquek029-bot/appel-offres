# preview_email.py
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plateforme_offres.settings')
django.setup()

from django.template.loader import render_to_string
from offres.models import AppelOffre
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.filter(role='EXPERT').first() or User.objects.filter(is_superuser=True).first()
offres = list(AppelOffre.objects.filter(mode_acquisition='AUTO')[:2])

html = render_to_string('emails/alerte_nouvelles_offres.html', {
    'user': user, 'offres': offres, 'keywords': 'informatique, route'
})

with open('email_preview.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("✅ Ouvrez 'email_preview.html' dans Chrome/Firefox")