from django.urls import path
from .views import Signup,LogoutUser,loginUser,UserProfile,Following,Settings

urlpatterns = [
    path('signup',Signup,name='signup'),
    path('loginuser',loginUser,name='login'),
    path('logout',LogoutUser,name='logout'),
    path('profile',UserProfile,name='profile'),
    path('<username>',UserProfile,name='profile'),
    path('<username>/saved',UserProfile,name='profilefavourite'),
    path('follow/<username>',Following,name='following'),
    path('cn/settings',Settings,name="settings") 

   
]