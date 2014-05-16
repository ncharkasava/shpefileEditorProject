from django.conf.urls import patterns, url, include
from django.contrib.gis import admin

from shapeEditor.editor.forms import ContactForm1, ContactForm2, ContactForm3
from shapeEditor.shared.views import ContactWizard

import settings


admin.autodiscover()

urlpatterns = patterns('',
	url(r'^editor/', include('shapeEditor.editor.urls')),
        url(r'^tms/', include('shapeEditor.tms.urls')),
        
        # user auth urls
        url(r'^editor/login/$',  'shapeEditor.shared.views.login'),
        url(r'^editor/auth/$',  'shapeEditor.shared.views.auth_view'),    
        url(r'^editor/logout/$', 'shapeEditor.shared.views.logout'),
        url(r'^editor/loggedin/$', 'shapeEditor.shared.views.loggedin'),
        url(r'^editor/invalid/$', 'shapeEditor.shared.views.invalid_login'),  
        url(r'^editor/about/$', 'shapeEditor.shared.views.about'),  
        url(r'^editor/help/$', 'shapeEditor.shared.views.help'),
        url(r'^editor/contact/$', 'shapeEditor.shared.views.contact'),
        url(r'^editor/register/$', 'shapeEditor.shared.views.register_user'),
        url(r'^editor/register_success/$', 'shapeEditor.shared.views.register_success'),
        url(r'^contact/$', ContactWizard.as_view([ContactForm1, ContactForm2, ContactForm3])),
)


urlpatterns += patterns('',
    # Examples:
    # url(r'^$', 'shapeEditor.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    (r'^admin/', include(admin.site.urls)),
    
)

if not settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
   
    urlpatterns += staticfiles_urlpatterns()
