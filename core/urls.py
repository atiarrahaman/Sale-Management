from django.urls import path
from .views import UserLoginView,user_logout, AdminHomeView,StaffHomeView
urlpatterns = [
    path('user_login/', UserLoginView.as_view(), name='user_login'),
    path('user_logout/', user_logout, name='user_logout'),
    path('admin_home/', AdminHomeView.as_view(), name='admin_home'),
    path('staff_home/', StaffHomeView.as_view(), name='staff_home'),

]
