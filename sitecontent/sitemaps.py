from django.contrib.sitemaps import Sitemap
from .models import Service, Project, Post
from django.urls import reverse


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Service.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.9

    def items(self):
        return Project.objects.all()

    def location(self, obj):
        return obj.get_absolute_url()


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Post.objects.filter(published=True)

    def location(self, obj):
        return obj.get_absolute_url()


class StaticSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return [
            "home",
            "services_list",
            "projects_list",
            "partners",
            "contact",
            "blog_list",
        ]

    def location(self, item):
        return reverse(item)
