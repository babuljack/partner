from django.shortcuts import render,get_object_or_404
from django.shortcuts import HttpResponse,HttpResponseRedirect,redirect,redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm,UserChangeForm,PasswordChangeForm
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Profile,User
from Main.models import Post,Follow,Stream
from django.urls import reverse,resolve
#from django.contrib.auth.models import User
from django.urls import reverse,resolve
from django.db import transaction
from .forms import SignUpForm,UserUpdateForm,LoginForm
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
# Create your views here.


def Signup(request):
  if not request.user.is_authenticated:
    if request.method=='POST':
        fm=SignUpForm(request.POST)
        if fm.is_valid():
            uname=fm.cleaned_data['username']
            upass=fm.cleaned_data['password2']
            register=fm.save()
            if register:
               user=authenticate(username=uname,password=upass)
               if user is not None:
                   login(request, user)
                   return HttpResponseRedirect('/')
            #messages.success(request, "User register successfully")
    else:
        fm=SignUpForm()
    return render(request,'accounts/signup.html',{'form':fm})
  else:
      return HttpResponseRedirect('/user/profile')  


def loginUser(request):
    if not request.user.is_authenticated:
        if request.method=="POST":
            fm=LoginForm(request=request,data=request.POST)
            if fm.is_valid():
                uname=fm.cleaned_data['username']
                upass=fm.cleaned_data['password']
                user=authenticate(username=uname,password=upass)
                if user is not None:
                    login(request,user)
                    try:
                        nextpage=request.GET['next']
                        if nextpage:

                            """Protacting From ssrf attacks"""                  
                            url_is_safe=url_has_allowed_host_and_scheme(url=nextpage,allowed_hosts=set(),
                            require_https=request.is_secure())           
                            if url_is_safe:
                                return HttpResponseRedirect(nextpage)
                            else:
                                return HttpResponseRedirect('/user/profile')

                            """default , Never use like this it's vulnerable."""
                            #return HttpResponseRedirect(nextpage)         

                    except:
                        return HttpResponseRedirect('/user/profile')               
        else:
            fm=LoginForm()
        return render(request,'accounts/login.html',{'form':fm})
    else:
        return HttpResponseRedirect('/user/profile')                  

def LogoutUser(request):
    if request.user.is_authenticated:
        logout(request)
        return HttpResponseRedirect('/user/loginuser')
    else:
        return HttpResponseRedirect('/user/loginuser')  

def UserProfile(request,username=None):
    if request.user.is_authenticated:
        try:
          profile=Profile.objects.get(user__username=username)
        except:
          profile=Profile.objects.get(user=request.user)
    
        url_name=resolve(request.path).url_name

        if url_name=='profile':
            posts=Post.objects.filter(user=profile.user)
        else:
            if request.user==profile.user:
               posts=profile.favourite.all()
            else:
               posts=Post.objects.filter(user=profile.user) 
        posts_count=Post.objects.filter(user=profile.user).count()
        following_counts=Follow.objects.filter(follower=profile.user).count()
        follower_counts=Follow.objects.filter(following=profile.user).count()
        follow_status=Follow.objects.filter(following=profile.user,follower=request.user).exists()        
        context={
            'profile':profile,
            'url_name':url_name,
            'posts':posts,
            'posts_count':posts_count,
            'follower_counts':follower_counts,
            'following_counts':following_counts,
            'follow_status':follow_status,
        }
        return render(request,'accounts/profile.html',context)
    else:
        return HttpResponseRedirect('/user/loginuser') 


def Following(request,username):
    following=get_object_or_404(User,username=username)
    user=request.user
    try:
       Follow.objects.get(follower=user,following=following).delete()
       oldstream=Stream.objects.filter(following=following,user=user)
       for stream in oldstream:
           stream.user.remove(user)
       #clean up
       streams=Stream.objects.filter(following=following)
       for stream in streams:
          users=stream.user.all()
          if not users.exists():
              stream.delete()     
     
    except:
       
       Follow.objects.create(follower=user,following=following).save()
       posts=Post.objects.all().filter(user=following)[:5]
       followers=Follow.objects.filter(following=following,follower=user)
       followlist=[]
       for follow in followers:
           followlist.append(follow.follower)   
       #with transaction.atomic():
       if followlist:
            for post in posts:
                stream=Stream.objects.create(following=following,post=post)
                stream.user.set(followlist)
                stream.save()
    #user=user        
    return HttpResponseRedirect(reverse('profile',args=[username]))   

def Settings(request):



    if request.GET.get('profile'):
        profile=Profile.objects.get(user=request.user)
        if request.method=='POST':
           try:
               pic=request.FILES['profile']
               if pic:
                  profile=User.objects.get(username=request.user)
                  profile.picture=pic
                  profile.save()
                  messages.success(request,'Picture Successfully Changed!')
           except:   
               bio=request.POST.get('bio')
               quotes=request.POST.get('quotes')
               address=request.POST.get('address')
               #connected
               website=request.POST.get('website')
               twitter=request.POST.get('twitter')  
               instragram=request.POST.get('instragram')  
               facebook=request.POST.get('facebook')  
               github=request.POST.get('github')
               info=Profile.objects.get(user=request.user)
               info.bio=bio
               info.quotes=quotes
               info.address=address
               info.website=website
               info.twitter=twitter
               info.instragram=instragram
               info.facebook=facebook
               info.github=github
               info.save()
               messages.success(request,'Information Updated!')            


        context={
            'active':'active',
            'profile':profile,
        }
        return render(request, 'accounts/profile/profile_change.html',context)

    if request.GET.get('password'):
        if request.method=="POST":
            fm=PasswordChangeForm(request.user, request.POST)
            if fm.is_valid():
                fm.save()
                messages.success(request,'Password Successfully Changed!')
        else:
            fm=PasswordChangeForm(request.user)

        context={
            'active':'active',
            'form':fm,
        }
        return render(request, 'accounts/profile/change_password.html',context)

    if request.GET.get('help'):
        context={
            'active':'active',
        }
        return render(request, 'accounts/profile/help.html',context)

    if request.GET.get('report'):
        context={
            'active':'active',
        }
        return render(request, 'accounts/profile/report.html',context)        


    if request.method=="POST":
        fname=request.POST.get('first_name')
        lname=request.POST.get('last_name')
        email=request.POST.get('email')
        db=request.POST.get('db')
        update=User.objects.get(username=request.user)
        update.first_name=fname
        update.last_name=lname
        update.email=email
        update.db=db
        update.save()
        data={
        'information':'Successfully Updated..'
        }
        return JsonResponse(data)

    return render(request,'accounts/profile/general.html',{'active':'active'})     
    
    



