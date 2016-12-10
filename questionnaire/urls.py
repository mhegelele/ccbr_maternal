from django.conf.urls import url

from questionnaire import views


urlpatterns = [
    url(r'^$', views.dashboard, name='dashboard'),
    url(r'^clients/followup/day7/$', views.followup_day7, name='followup-day7'),
    url(r'^clients/followup/day28/$', views.followup_day28, name='followup-day28'),
    url(r'^clients/followup/reminders/$', views.followup_day3, name='reminders'),
    url(r'^forms/$', views.form_listing, name='form-listing'),
    url(r'^new/$', views.manage_form, name='form-create'),
    url(r'^(?P<slug>[-\w]+)/$', views.manage_form, name='form-update'),
    url(r'^(?P<slug>[-\w]+)/editor/$', views.form_editor, name='form-editor'),
    url(r'^(?P<slug>[-\w]+)/data/$', views.data_listing, name='data-listing'),
    url(r'^(?P<slug>[-\w]+)/export/$', views.export_form_data, name='data-export'),
    url(r'^(?P<slug>[-\w]+)/new$', views.form_display, name='data-create'),
    url(r'^(?P<slug>[-\w]+)/(?P<uuid>[-\w]+)/$', views.form_display, name='data-update'),
]
