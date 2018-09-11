from django.conf.urls import url
from django.contrib import admin
from core import views
from django.contrib.auth import views as auth_views
from .views import EditPersonalInfoView, EditFinancialInfoView

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^account-setup/$', views.account_setup, name='account-setup'),
    url(r'^history/$', views.history, name='history'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^financials/$', views.financials, name='financials'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^edit-profile/', EditPersonalInfoView.as_view(), name="edit_profile"),
    url(r'^edit-financials/', EditFinancialInfoView.as_view(), name="edit-financials"),
    url(r'^lease-apply/$', views.lease_apply, name='lease-apply'),
    url(r'^join-group/$', views.join_group, name='join-group'),
    url(r'^viewinfo/(?P<share_key>[^/]+)/$', views.leaser_view, name='leaser_view'),
    url(r'^superadmin/$', views.superadmin, name='superadmin')
]
