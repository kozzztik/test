from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
from django.contrib import admin
from .views import HomeView, DetailsView, EditView

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^details/$', DetailsView.as_view(), name='details'),
    url(r'^edit/$', EditView.as_view(), name='edit'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
             {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
    urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )