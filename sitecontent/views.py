from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from .models import HomeSettings, Service, Project, Partner, Post
from .forms import ContactForm


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
    return render(request, "services_list.html", {"services": Service.objects.all()})


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    return render(request, "service_detail.html", {"service": service})


def projects_list(request):
    return render(request, "projects_list.html", {"projects": Project.objects.all()})


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, "project_detail.html", {"project": project})


def partners_view(request):
    return render(request, "partners.html", {"partners": Partner.objects.all()})


def blog_list(request):
    return render(
        request, "blog_list.html", {"posts": Post.objects.filter(published=True)}
    )


def blog_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, published=True)
    return render(request, "blog_detail.html", {"post": post})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
    if form.is_valid():
        form.send_email()
        csv_bytes = form.to_csv_bytes()
        resp = HttpResponse(csv_bytes, content_type="text/csv")
        resp["Content-Disposition"] = 'attachment; filename="contact.csv"'
        return resp
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form})
