from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='index'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('user-management/', views.user_management, name='user_management'),
    path('update-user-status/', views.update_user_status, name='update_user_status'),
    path('admin-requests/', views.admin_requests, name='admin_requests'),
    path('admin-accept-request/', views.accept_certificate_request, name='accept_certificate_request'),
    path('admin-reject-request/', views.reject_certificate_request, name='reject_certificate_request'),
    
    
    path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
    path('user/new-certificate-request/', views.new_certificate_request, name='new_certificate_request'),
    path('user/submit-certificate-request/', views.submit_certificate_request, name='submit_certificate_request'),
    path('user/certificates/', views.my_certificates, name='my_certificates'),
    path('user/certificate/download/<int:certificate_id>/', views.download_certificate, name='download_certificate'),
    path('user/certificate/delete/<int:certificate_id>/', views.delete_certificate, name='delete_certificate'),
    
    path('user/request-status/', views.request_status, name='request_status'),
    path('user/request/<int:request_id>/', views.request_detail, name='request_detail'),
    
    
]
