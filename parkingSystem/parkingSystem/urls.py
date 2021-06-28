"""test_smartPark URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from myapp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('main/',views.main,name="main"),
    path('',views.userLogin,name=""),
    path('adminLogin/',views.adminLogin,name="adminLogin"),
    path('adminMain/',views.adminMain,name="adminMain"),
    path('signUp/',views.signUp,name="signUp"),
    path('logout/',views.logout,name="logout"),
    path('contact/',views.contact,name="contact"),
    path('profile/',views.profile,name="profile"),
    path('history/',views.history,name="history"),
    path('historyAdmin/',views.historyAdmin,name="historyAdmin"),
]
