from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.sitemaps.views import sitemap
from sitecontent.sitemaps import (
    ServiceSitemap,
    ProjectSitemap,
    PostSitemap,
    StaticSitemap,
)
from django.views.static import serve as static_serve


sitemaps = {
    "services": ServiceSitemap,
    "projects": ProjectSitemap,
    "posts": PostSitemap,
    "static": StaticSitemap,
}


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("sitecontent.urls")),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("ckeditor/", include("ckeditor_uploader.urls")),
]


urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        static_serve,
        {"document_root": settings.MEDIA_ROOT, "show_indexes": False},
        name="media",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
