from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('auth_app.urls')), # auth_app URL'larini qo'shish
                                       # Yoki path('auth/', include('auth_app.urls')) kabi
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)