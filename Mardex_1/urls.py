from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from client.views import confirm_order

urlpatterns = [
    path('admin/', admin.site.urls),
    path('client/', include('client.urls')),
    path('worker/', include('worker.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),  # OAuth2 uchun URL
    path('confirm_order/<int:order_id>/', confirm_order, name='confirm_order'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

