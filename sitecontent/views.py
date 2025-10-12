from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse
from .models import HomeSettings, Service, Project, Partner, Post
from .forms import ContactForm


def about(request):
    return render(request, "about.html")


def home(request):
    settings = HomeSettings.objects.first() or HomeSettings.objects.create()
    services = Service.objects.all()[:6]
    projects = Project.objects.all()[:6]
    partners = Partner.objects.all()
    posts = Post.objects.filter(published=True)[:3]
    return render(
        request,
        "home.html",
        {
            "settings": settings,
            "services": services,
            "projects": projects,
            "partners": partners,
            "posts": posts,
        },
    )


def services_list(request):
    qs = Service.objects.all()

    q = (request.GET.get("q") or "").strip()
    sort = (request.GET.get("sort") or "").strip()

    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(excerpt__icontains=q) | Q(body__icontains=q)
        )

    if sort in {"title", "-updated"}:
        qs = qs.order_by(sort)
    else:
        qs = qs.order_by("title")

    return render(request, "services_list.html", {"services": qs})


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    return render(request, "service_detail.html", {"service": service})


def projects_list(request):
    qs = Project.objects.all().prefetch_related("images")

    # --- Query params (GET) ---
    q = (request.GET.get("q") or "").strip()
    client = (request.GET.get("client") or "").strip()
    location = (request.GET.get("location") or "").strip()
    year = (request.GET.get("year") or "").strip()
    sort = (request.GET.get("sort") or "").strip()

    # --- Recherche plein texte simple ---
    if q:
        qs = qs.filter(
            Q(title__icontains=q)
            | Q(client__icontains=q)
            | Q(location__icontains=q)
            | Q(context__icontains=q)
            | Q(solution__icontains=q)
            | Q(results__icontains=q)
        )

    # --- Filtres ---
    if client:
        qs = qs.filter(client__icontains=client)
    if location:
        qs = qs.filter(location__icontains=location)
    if year:
        qs = qs.filter(year__icontains=year)

    # --- Tri ---
    allowed_sorts = {
        "-year": "-year",
        "year": "year",
        "title": "title",
        "-created": "-created",  # fallback technique
    }
    if sort in allowed_sorts:
        qs = qs.order_by(allowed_sorts[sort])
    else:
        qs = qs.order_by("-created", "title")  # tri recommandé par défaut

    # --- Pagination ---
    page = request.GET.get("page", "1")
    paginator = Paginator(qs, 9)  # 9 cartes / page
    try:
        page_obj = paginator.get_page(page)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    context = {
        "projects": page_obj.object_list,  # utilisé par le template
        "page_obj": page_obj,  # pagination (optionnelle dans le template)
    }
    return render(request, "projects_list.html", context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, "project_detail.html", {"project": project})


def partners_view(request):
    return render(request, "partners.html", {"partners": Partner.objects.all()})


def blog_list(request):
    qs = Post.objects.filter(published=True)

    q = (request.GET.get("q") or "").strip()
    year = (request.GET.get("year") or "").strip()
    sort = (request.GET.get("sort") or "").strip()

    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(body__icontains=q))

    if year.isdigit():
        qs = qs.filter(pub_date__year=int(year))

    # Tri autorisé
    allowed_sorts = {"-pub_date", "pub_date", "title"}
    if sort in allowed_sorts:
        qs = qs.order_by(sort)

    paginator = Paginator(qs, 9)  # 9 cartes par page
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "blog_list.html",
        {
            "posts": page_obj.object_list,
            "page_obj": page_obj,
            "is_paginated": page_obj.has_other_pages(),
        },
    )


def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)

    prev_post = (
        Post.objects.filter(published=True, pub_date__lt=post.pub_date)
        .order_by("-pub_date")
        .first()
    )
    next_post = (
        Post.objects.filter(published=True, pub_date__gt=post.pub_date)
        .order_by("pub_date")
        .first()
    )
    recent_posts = (
        Post.objects.filter(published=True)
        .exclude(pk=post.pk)
        .order_by("-pub_date")[:5]
    )

    return render(
        request,
        "blog_detail.html",
        {
            "post": post,
            "prev_post": prev_post,
            "next_post": next_post,
            "recent_posts": recent_posts,
        },
    )


def contact(request):
    """
    GET  -> affiche le formulaire
    POST -> valide, envoie l'email et retourne un CSV (ou ré-affiche erreurs)
    """
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Envoi email
            form.send_email()

            # Option: message flash (si tu préfères rediriger au lieu de renvoyer un CSV)
            # messages.success(request, "Merci ! Votre message a bien été envoyé.")

            # Retourner un CSV téléchargeable
            csv_bytes = form.to_csv_bytes()
            resp = HttpResponse(csv_bytes, content_type="text/csv")
            resp["Content-Disposition"] = 'attachment; filename="contact.csv"'
            return resp
        # si non valide -> on tombe en bas et on ré-affiche le formulaire avec erreurs
    else:
        form = ContactForm()

    return render(request, "contact.html", {"form": form})
