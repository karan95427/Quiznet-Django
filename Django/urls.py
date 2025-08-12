from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('aiquiz.urls', namespace='aiquiz')),  # Your app URLs

    # Password reset views (Django built-in)
    path('accounts/password/reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='account/pass_reset_form.html'
         ), 
         name='password_reset'),

    path('accounts/password/reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='account/pass_reset_done.html'
         ), 
         name='password_reset_done'),

    path('accounts/password/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='account/pass_reset_from_key.html'  # <--- match your file name!
         ),
         name='password_reset_confirm'),

    path('accounts/password/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='account/pass_reset.html'
         ),
         name='password_reset_complete'),

    path('accounts/', include('allauth.urls')),  # For django-allauth
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])