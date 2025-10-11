from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class TimeStamped(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class HomeSettings(TimeStamped):
    hero_title = models.CharField(
        max_length=160, default="Ingénierie • Industriel • TP"
    )
    hero_subtitle = models.CharField(max_length=255, blank=True)
    hero_cta_label = models.CharField(
        max_length=60, blank=True, default="Demander un devis"
    )
    hero_cta_url = models.CharField(max_length=200, blank=True, default="#contact")
    stat_1_label = models.CharField(
        max_length=80, blank=True, default="Années d'expérience"
    )
    stat_1_value = models.CharField(max_length=40, blank=True, default="10+")
    stat_2_label = models.CharField(max_length=80, blank=True, default="Projets livrés")
    stat_2_value = models.CharField(max_length=40, blank=True, default="50+")
    stat_3_label = models.CharField(max_length=80, blank=True, default="Partenaires")
    stat_3_value = models.CharField(max_length=40, blank=True, default="TCA…")

    class Meta:
        verbose_name = _("Paramètres d'accueil")
        verbose_name_plural = _("Paramètres d'accueil")

        def __str__(self):
            return "Accueil"


class Partner(TimeStamped):
    name = models.CharField(max_length=120)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="partners/", blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Service(TimeStamped):
    title = models.CharField(max_length=140)
    slug = models.SlugField(unique=True)
    excerpt = models.TextField(blank=True)
    body = models.TextField(blank=True)
    icon = models.CharField(
        max_length=60, blank=True, help_text="Nom d’icône (optionnel)"
    )
    cover = models.ImageField(upload_to="services/", blank=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("service_detail", args=[self.slug])


class Project(TimeStamped):
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    client = models.CharField(max_length=160, blank=True)
    location = models.CharField(max_length=160, blank=True)
    year = models.CharField(max_length=10, blank=True)
    context = models.TextField(blank=True)
    solution = models.TextField(blank=True)
    results = models.TextField(blank=True)
    cover = models.ImageField(upload_to="projects/", blank=True)
    gallery = models.ManyToManyField("ProjectImage", blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project_detail", args=[self.slug])


class ProjectImage(models.Model):
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=160, blank=True)

    def __str__(self):
        return self.caption or self.image.name


class Post(TimeStamped):
    title = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    published = models.BooleanField(default=True)
    pub_date = models.DateField(auto_now_add=True)
    cover = models.ImageField(upload_to="blog/", blank=True)

    class Meta:
        ordering = ["-pub_date"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("blog_detail", args=[self.slug])
