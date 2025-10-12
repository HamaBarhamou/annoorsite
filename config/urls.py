from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from sitecontent.sitemaps import (
    ServiceSitemap,
    ProjectSitemap,
    PostSitemap,
    StaticSitemap,
)


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


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
