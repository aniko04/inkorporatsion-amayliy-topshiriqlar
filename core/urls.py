"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.views.static import serve
from django.views.decorators.clickjacking import xframe_options_sameorigin
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('index.html', views.home, name='index'),

    # Platformaning yetti bo'limi (navbar)
    path('haqida', views.haqida, name='haqida'),
    path('metodika', views.metodika, name='metodika'),
    path('maqola', views.maqola, name='maqola'),
    path('multimediya', views.multimediya, name='multimediya'),
    path('topshiriq', views.topshiriq, name='topshiriq'),
    path('topshiriq/rasmli-test', views.rasmli_test_sahifa, name='rasmli_test'),
    path('topshiriq/diktantlar', views.diktant_sahifa, name='diktant'),
    path('xarita', views.xarita, name='xarita'),
    path('xarita/qalamdon', views.qalamdon_sahifa, name='qalamdon'),
    path('xarita/xonqizi', views.xonqizi_sahifa, name='xonqizi'),
    path('ishlanma', views.ishlanma, name='ishlanma'),

    # Administrator sahifasi — barcha foydalanuvchilar va ularning natijalari.
    # `admin_required` ichkarida: xodim bo'lmagan kishi bosh sahifaga qaytadi.
    path('oquvchilarim', views.oquvchilarim, name='oquvchilarim'),
    path('oquvchilarim/eksport', views.oquvchilarim_eksport, name='oquvchilarim_eksport'),
    path('oquvchilarim/<int:pk>', views.oquvchi_natija, name='oquvchi_natija'),

    # Auth
    path('login', views.login_view, name='login'),
    path('register', views.register_view, name='register'),
    path('logout', views.logout_view, name='logout'),
    path('api/save-result', views.save_result, name='save_result'),
    
    # Qisqa URL lar
    path('m1', views.mashq1, name='mashq1'),
    path('m2', views.mashq2, name='mashq2'),
    path('m3', views.mashq3, name='mashq3'),
    path('m4', views.mashq4, name='mashq4'),
    path('m5', views.mashq5, name='mashq5'),
    path('m6a', views.mashq6a, name='mashq6a'),
    path('m6b', views.mashq6b, name='mashq6b'),
    path('m6c', views.mashq6c, name='mashq6c'),

    # O'quvchi uchun 6-mashq (talaba bilan bir xil format, alohida sahifalar)
    path('o6a', views.oquvchi_m6a, name='oquvchi_m6a'),
    path('o6b', views.oquvchi_m6b, name='oquvchi_m6b'),
    path('o6c', views.oquvchi_m6c, name='oquvchi_m6c'),
    path('o7a', views.oquvchi_m7a, name='oquvchi_m7a'),
    path('o7b', views.oquvchi_m7b, name='oquvchi_m7b'),
    path('o7c', views.oquvchi_m7c, name='oquvchi_m7c'),
    path('o8a', views.oquvchi_m8a, name='oquvchi_m8a'),
    path('o8b', views.oquvchi_m8b, name='oquvchi_m8b'),
    path('o8c', views.oquvchi_m8c, name='oquvchi_m8c'),
    path('o9a', views.oquvchi_m9a, name='oquvchi_m9a'),
    path('o9a2', views.oquvchi_m9a2, name='oquvchi_m9a2'),
    path('o9b', views.oquvchi_m9b, name='oquvchi_m9b'),
    path('o9c', views.oquvchi_m9c, name='oquvchi_m9c'),
    path('o10a', views.oquvchi_m10a, name='oquvchi_m10a'),
    path('o10b', views.oquvchi_m10b, name='oquvchi_m10b'),
    path('o10c', views.oquvchi_m10c, name='oquvchi_m10c'),

    path('m7a', views.mashq7a, name='mashq7a'),
    path('m7b', views.mashq7b, name='mashq7b'),
    path('m7c', views.mashq7c, name='mashq7c'),
    path('m8a', views.mashq8a, name='mashq8a'),
    path('m8b', views.mashq8b, name='mashq8b'),
    path('m8c', views.mashq8c, name='mashq8c'),
    path('m9a', views.mashq9a, name='mashq9a'),
    path('m9a2', views.mashq9a2, name='mashq9a2'),
    path('m9b', views.mashq9b, name='mashq9b'),
    path('m9c', views.mashq9c, name='mashq9c'),
    path('m10a', views.mashq10a, name='mashq10a'),
    path('m10b', views.mashq10b, name='mashq10b'),
    path('m10c', views.mashq10c, name='mashq10c'),
    
    # Eski URL lar (backward compatibility)
    path('mashq1.html', views.mashq1, name='mashq1_html'),
    path('mashq2.html', views.mashq2, name='mashq2_html'),
    path('mashq3.html', views.mashq3, name='mashq3_html'),
    path('mashq4.html', views.mashq4, name='mashq4_html'),
    path('mashq5.html', views.mashq5, name='mashq5_html'),
    path('mashq6a.html', views.mashq6a, name='mashq6a_html'),
    path('mashq6b.html', views.mashq6b, name='mashq6b_html'),
    path('mashq6c.html', views.mashq6c, name='mashq6c_html'),
    path('mashq7a.html', views.mashq7a, name='mashq7a_html'),
    path('mashq7b.html', views.mashq7b, name='mashq7b_html'),
    path('mashq7c.html', views.mashq7c, name='mashq7c_html'),
    path('mashq8a.html', views.mashq8a, name='mashq8a_html'),
    path('mashq8b.html', views.mashq8b, name='mashq8b_html'),
    path('mashq8c.html', views.mashq8c, name='mashq8c_html'),
    path('mashq9a.html', views.mashq9a, name='mashq9a_html'),
    path('mashq9a2.html', views.mashq9a2, name='mashq9a2_html'),
    path('mashq9b.html', views.mashq9b, name='mashq9b_html'),
    path('mashq9c.html', views.mashq9c, name='mashq9c_html'),
    path('mashq10a.html', views.mashq10a, name='mashq10a_html'),
    path('mashq10b.html', views.mashq10b, name='mashq10b_html'),
    path('mashq10c.html', views.mashq10c, name='mashq10c_html'),
]

# Statikni WhiteNoise (middleware) beradi — bu yerda URL kerak emas.
# Media esa runtime'da yuklanadi, shuning uchun path() konverteri orqali beriladi.
#
# `xframe_options_sameorigin`: XFrameOptionsMiddleware standart holda har bir
# javobga `X-Frame-Options: DENY` qo'yadi, shu sababli /haqida sahifasidagi PDF
# ko'ruvchi (<iframe>) ochilmay, brauzer "refused to connect" deb yozardi.
# Faqat media uchun SAMEORIGIN qilamiz — o'z saytimiz ramkaga sola oladi,
# begona saytlar esa baribir sola olmaydi. Qolgan sahifalar DENY bo'lib qoladi.
urlpatterns += [
    path('media/<path:path>', xframe_options_sameorigin(serve),
         {'document_root': settings.MEDIA_ROOT}),
]
