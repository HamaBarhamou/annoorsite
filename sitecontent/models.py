from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


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
    hero_bg = models.ImageField(upload_to="home/", blank=True)
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

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("project_detail", args=[self.slug])


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, related_name="images", on_delete=models.CASCADE, null=True, blank=True
    )
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


class SiteContact(models.Model):
    # Identité
    company_name = models.CharField("Raison sociale", max_length=160, default="ANNOOR")
    email = models.EmailField("Email de contact", blank=True)
    phone = models.CharField(
        "Téléphone",
        max_length=40,
        blank=True,
        help_text="+227 …",
        validators=[RegexValidator(r"^[0-9+\-\s().]+$", "Format téléphone invalide.")],
    )
    whatsapp = models.CharField(
        "WhatsApp (numéro)",
        max_length=40,
        blank=True,
        help_text="Ex: 22790000000 (chiffres uniquement si possible)",
        validators=[
            RegexValidator(r"^[0-9]+$", "Chiffres uniquement (indicatif compris).")
        ],
    )

    # Adresse
    address = models.CharField("Adresse (ligne 1)", max_length=200, blank=True)
    city = models.CharField("Ville", max_length=100, blank=True, default="Niamey")
    country = models.CharField("Pays", max_length=100, blank=True, default="Niger")

    # Présence en ligne
    website = models.URLField("Site web", blank=True)
    facebook = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    x_twitter = models.URLField("X / Twitter", blank=True)

    # Divers
    hours = models.CharField(
        "Horaires", max_length=160, blank=True, default="Lun–Ven, 9h–18h (GMT+1)"
    )
    map_embed_url = models.URLField("Google Maps Embed URL", blank=True)

    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Coordonnées du site"
        verbose_name_plural = "Coordonnées du site"

    def __str__(self):
        return f"{self.company_name} — {self.city or ''}".strip()

    @property
    def whatsapp_url(self):
        if not self.whatsapp:
            return ""
        # wa.me exige des chiffres uniquement
        digits = "".join([c for c in self.whatsapp if c.isdigit()])
        return f"https://wa.me/{digits}" if digits else ""
