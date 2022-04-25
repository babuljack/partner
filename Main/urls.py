from django.urls import path
from .views import PostDetails,Index,Like,Tags,favourite,CreatePost,PostShare,Notifications,Construction,Newstory,Test
import uuid
urlpatterns = [
    path('',Index,name='index'),
    path('PostDetail/<uuid:id>',PostDetails,name="postdetails"),
    path('likes/<uuid:id>',Like,name='likes'),
    path('tags/<str:slug>',Tags,name='tags'),
    path('favourite/<uuid:id>',favourite,name='favourite'),
    path('createpost',CreatePost,name='createpost'),
    path('share/<uuid:id>',PostShare,name='share'),
    path('notifications',Notifications,name="notification"),
    path('notifications/<int:pk>',Notifications,name="notification"),
    path('working',Construction,name='working'),
    path('story',Newstory,name='story'),
    path('testing',Test)

]