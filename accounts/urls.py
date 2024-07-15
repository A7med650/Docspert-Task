from django.urls import path

from . import views

urlpatterns = [
    path('', views.upload_accounts, name="upload_accounts"),
    path('accounts/', views.account_list, name="accounts"),
    path('account-detail/<pk>/', views.account_detail, name="account_detail"),
    path('transfer/',views.transfer,name="transfer"),
]