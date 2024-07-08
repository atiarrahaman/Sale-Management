from django.urls import path
from .views import user_logout, AdminHomeView, StaffCreateView, AllStaffView, StaffProfile, ProfileUpdateView, user_login
from .views import CustomPasswordChangeView
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('user_login/', user_login, name='user_login'),
    path('user_logout/', user_logout, name='user_logout'),
    path('admin_home/', AdminHomeView.as_view(), name='admin_home'),
    path('add_staff/', StaffCreateView.as_view(), name='add_staff'),
    path('all_staff/', AllStaffView.as_view(), name='all_staff'),
    path('profile/', StaffProfile.as_view(), name='profile'),
    path('edit_profile/', ProfileUpdateView.as_view(), name='edit_profile'),
    path('password_change/', CustomPasswordChangeView.as_view(),
         name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),
]

