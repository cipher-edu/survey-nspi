from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('auth_app.urls')), # auth_app URL'larini qo'shish
                                       # Yoki path('auth/', include('auth_app.urls')) kabi
]

# Development rejimida static va media fayllar uchun URL'lar
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)