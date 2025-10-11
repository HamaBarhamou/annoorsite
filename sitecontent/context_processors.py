# sitecontent/context_processors.py
from .models import SiteContact


def site_contact(request):
    return {"site_contact": SiteContact.objects.first()}
