from django.contrib import admin
from django.urls import path, include
from accounts.views import home_view  

urlpatterns = [
    path('', home_view),              
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('problems/', include('problems.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
]
