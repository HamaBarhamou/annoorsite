# sitecontent/context_processors.py
from .models import SiteContact, Service


def site_contact(request):
    contact = SiteContact.objects.first()
    # On expose quelques services pour le mega-menu (ne casse rien si vide)
    nav_services = Service.objects.order_by("title")[:6]
    return {
        "site_contact": contact,
        "nav_services": nav_services,
    }
