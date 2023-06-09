from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include("chat.urls")),
    path('campaigns/', include("campaigns.urls")),
    path('users/', include('allauth.urls')),  #소셜로그인
    path('users/', include("users.urls")),
    path('payments/', include("payments.urls")),    
    path('shop/', include("shop.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
