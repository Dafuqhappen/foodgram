from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch

from api.views import RecipeViewSet

def short_link_redirect(request, pk):
    """
    Редирект короткой ссылки на канонический URL рецепта.
    """
    try:
        target = reverse("api:recipes-detail", kwargs={"pk": pk})
    except NoReverseMatch:
        target = f"/recipes/{pk}/"
    return redirect(target, permanent=False)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('api.urls', 'api'), namespace='api')),
    path(
        's/<int:pk>/',
        short_link_redirect,
        name="recipe-short-link",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += staticfiles_urlpatterns()
