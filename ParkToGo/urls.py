from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ParkToGo.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^parktogo/', include('mainpage.urls', namespace = 'mainpage')),

    url(r'^admin/', include(admin.site.urls)),
)
