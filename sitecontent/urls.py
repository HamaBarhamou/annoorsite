from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("services/", views.services_list, name="services_list"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("projects/", views.projects_list, name="projects_list"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("partners/", views.partners_view, name="partners"),
    path("blog/", views.blog_list, name="blog_list"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("contact/", views.contact, name="contact"),
    path("contact/merci/", views.contact_thanks, name="contact_thanks"),
    path("about/", views.about, name="about"),
]
