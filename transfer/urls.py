from django.conf.urls import patterns, include, url
from myauth.views import *
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

#urlpatterns = patterns('',
transfer_patterns = patterns('',
    # Examples:
    # url(r'^$', 'transfer.views.home', name='home'),
    # url(r'^transfer/', include('transfer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),


    #url(r'^explorer/',   include('explorer.urls', namespace='explorer')),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^logout', mylogout_view, name='mylogout'),
    #url(r'^sampler/',   include('myexplorer.urls', namespace='myexplorer')),

    # direct domain
    url(r'^',   include('myexplorer.urls', namespace='myexplorer')),

    #url(r'^transfer/',   include('myexplorer.urls', namespace='myexplorer')),
    #url(r'^',               redirect_to, {'url': '/transfer/'})
    #url(r'^',               RedirectView.as_view(url='/transfer/'))
    #url(r'^', test_view, name='default'),
)

urlpatterns = patterns('',
    #url(r'^transfer/',          include(transfer_patterns)),
    url(r'^',               include(transfer_patterns)),
    #url(r'^',               RedirectView.as_view(url='/transfer/'))
)

