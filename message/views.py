from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from .models import Message
from Account.models import User
from django.db.models import Max
from django.db.models import Q
# Create your views here.
def UserMessage(request): 
	users=None
	Inbox=None
	chat_name=None
	users=Message.get_messages(user=request.user)

	messages=None		      	
	if request.GET.get('user'):
		try:
           
			name=request.GET.get('user')
			user=request.user
			rp=User.objects.get(username=name)
			if user == rp:
				Inbox=None
			else:
				Inbox=rp		
				messages=Message.objects.filter(user=user,recipient=rp)
				messages.update(is_read=True)
				chat_name=name

				
		except:
			Inbox=None	
	
	context={
	'users':users,
	'messages':messages,
	'Inbox':Inbox,
	'chat_name':chat_name
	}

	return render(request,'message/direct.html',context)



def SendDirect(request):
	from_user = request.user
	to_user_username = request.POST.get('to_user')
	body = request.POST.get('body')
	
	if request.method == 'POST':
		to_user = User.objects.get(username=to_user_username)
		Message.send_message(from_user, to_user, body)
		redirect=f'msg?user={to_user_username}'
		return HttpResponseRedirect(redirect)
	else:
		HttpResponseBadRequest()
	
	