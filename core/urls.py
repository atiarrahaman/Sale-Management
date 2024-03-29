from django.urls import path
from .views import UserLoginView, user_logout, AdminHomeView, StaffCreateView, AllStaffView
urlpatterns = [
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', user_logout, name='user_logout'),
    path('admin_home/', AdminHomeView.as_view(), name='admin_home'),

    path('add_staff/', StaffCreateView.as_view(), name='add_staff'),
    path('all_staff/', AllStaffView.as_view(), name='all_staff'),


]
