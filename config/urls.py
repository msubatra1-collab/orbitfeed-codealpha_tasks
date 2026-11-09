import json
from pathlib import Path

from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static


def routes_manifest(request):
    manifest = (Path(settings.BASE_DIR) / "public" / "manus-routes.json").read_text(encoding="utf-8")
    return HttpResponse(manifest, content_type="application/json; charset=utf-8")


def robots_txt(request):
    return HttpResponse("User-agent: *\nAllow: /\n", content_type="text/plain; charset=utf-8")


urlpatterns = [
    path("manus-routes.json", routes_manifest, name="routes_manifest"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("admin/", admin.site.urls),
    path("accounts/", include("users.urls")),
    path("orders/", include("orders.urls")),
    path("", include("store.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
