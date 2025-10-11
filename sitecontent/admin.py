from django.contrib import admin
from .models import (
    HomeSettings,
    Partner,
    Service,
    Project,
    ProjectImage,
    Post,
    SiteContact,
)


@admin.register(HomeSettings)
class HomeSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Hero",
            {
                "fields": (
                    "hero_title",
                    "hero_subtitle",
                    "hero_cta_label",
                    "hero_cta_url",
                    "hero_bg",
                )
            },
        ),
        (
            "Stats",
            {
                "fields": (
                    "stat_1_label",
                    "stat_1_value",
                    "stat_2_label",
                    "stat_2_value",
                    "stat_3_label",
                    "stat_3_value",
                )
            },
        ),
    )


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ("name", "website")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "updated")
    search_fields = ("title", "excerpt", "body")


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 2
    fields = ("image", "caption")
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProjectImageInline]
    list_display = ("title", "client", "year", "updated")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "published", "pub_date")
    list_filter = ("published",)
    search_fields = ("title", "body")


@admin.register(SiteContact)
class SiteContactAdmin(admin.ModelAdmin):
    list_display = ("company_name", "phone", "email", "updated")
    fieldsets = (
        ("Identité", {"fields": ("company_name", "email", "phone", "whatsapp")}),
        ("Adresse", {"fields": ("address", "city", "country")}),
        (
            "Présence en ligne",
            {"fields": ("website", "facebook", "linkedin", "x_twitter")},
        ),
        ("Informations", {"fields": ("hours", "map_embed_url")}),
    )

    # Limite à 1 enregistrement (singleton “soft”)
    def has_add_permission(self, request):
        if SiteContact.objects.exists():
            return False
        return super().has_add_permission(request)
