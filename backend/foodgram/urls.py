from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import include, path
from django.shortcuts import redirect, get_object_or_404
from recipes.models import Recipe


def short_link_redirect(request, code):
    """
    Редирект с короткой ссылки вида /s/<code>/ на страницу рецепта.
    """
    recipe = get_object_or_404(Recipe, short_link=code)
    # Редирект на фронтовый роут SPA
    target = f"/recipes/{recipe.id}"
    return redirect(target, permanent=False)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(('api.urls', 'api'), namespace='api')),
    path(
        's/<str:code>/',
        short_link_redirect,
        name="recipe-short-link",
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += staticfiles_urlpatterns()
