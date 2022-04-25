from django.urls import path

from .views import UserMessage,SendDirect
urlpatterns=[

 path('',UserMessage,name='message'),
 path('send',SendDirect,name='senddirect')
]