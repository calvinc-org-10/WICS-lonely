"""django_support URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

######
## look to WICS for guidance on app startup if this goes client-server / multiuser
######

from django.contrib import admin
from django.urls import include, path
# from incShip import views
# from incShip import userinit


urlpatterns = [
    # path('', views.home, name='home'), # - this was the one constructed by Vis Stu
    # path('', userinit.inituser , name='initWICSuser'),
    # path('contact/', views.contact, name='contact'),
    # path('about/', views.about, name='about'),

    # path('menu/', include("cMenu.urls")),
    # path('util/', include("cMenu.utilurls")),
    # path('incShip/', include("incShip.urls")),
    
    path('admin/', admin.site.urls),
]