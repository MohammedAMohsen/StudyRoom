from django.urls import path
from django.contrib.auth import views as user_views
from . import views

urlpatterns = [
    # Function-Based Authentication Views
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_page, name='register'),

    # class-Based Reset_Password Views
    path('password-reset/',
        user_views.PasswordResetView.as_view(template_name='base/password_reset.html'),
        name='password_reset'
    ),
    path('password-reset-done/',
        user_views.PasswordResetDoneView.as_view(template_name='base/password_reset_done.html'),
        name='password_reset_done'
        ),
    path('password-reset-confirm/<uidb64>/<token>/',
        user_views.PasswordResetConfirmView.as_view(template_name='base/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path('password-reset-complete/',
        user_views.PasswordResetCompleteView.as_view(template_name='base/password_reset_complete.html'),
        name='password_reset_complete'
    ),

    # Function-Based Views
    path('', views.home, name='home'),
    path('room/<str:pk>/', views.room, name='room'), 
    path('user-profile/<str:pk>/', views.user_profile, name='user-profile'),
    path('create-room/', views.create_room, name='create-room'), 
    path('update-room/<str:pk>/', views.update_room, name='update-room'),
    path('delete-room/<str:pk>/', views.delete_room, name='delete-room'),
    path('delete-message/<str:pk>/', views.delete_message, name='delete-message'),
    path('update-user/', views.update_user, name='update-user'),
    path('topics/', views.topics, name='topics'),
    path('activityes/', views.activityes, name='activityes'),
]