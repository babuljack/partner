from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.http import JsonResponse
from .models import Post,Likes,Tag,Follow,Stream,Comment,Notification,Story
from django.contrib.auth.decorators import login_required
from django.urls import reverse,resolve
from Account.models import Profile
from .forms import PostForm,CommentForm,StoryForm
import re
from django.contrib import messages
from Account.models import User
from django.db.models import Q
# Create your views here.


@login_required(login_url='/user/loginuser')
def Index(request):
    
    #follow
    suggestfollow=None
    profile=None
    follower=Follow.objects.filter(following=request.user).order_by('-id')[:6]
    Followed=Follow.objects.filter(follower=request.user)
    #following_counts=Follow.objects.filter(follower=profile.user).count()
    following_user=[]
    for f in Followed:
        user=f.following
        following_user.append(user)
    suggestfollow=Profile.objects.filter(~Q(user__in=following_user),~Q(user=request.user))[:4]  

    #steaming
    stream=Stream.objects.filter(user=request.user).order_by('-date')
    if stream:
       pass
    else:
       stream=Stream.objects.filter(following=request.user).order_by('-date')
    posts={}
    for st in stream:
        #post=Post.objects.get(user=st.post.user,id=st.post.id)
        like=Likes.objects.filter(user=request.user,post=st.post).count()
        profile=Profile.objects.get(user=request.user)
        favourite=profile.favourite.filter(id=st.post.id).count()
        comment_count=Comment.totalcomments(post=st.post)
        sharecount=0
        shared=False
        try:
            scount=Post.objects.filter(share=st.post.id).count()
            if scount > 0:
                sharecount=scount
                share=Post.objects.filter(share=st.post.id)
                shared=share.filter(user=request.user).exists()
            else:    
                shareid=st.post.share.id
                share=Post.objects.filter(share=shareid)
                sharecount=share.count()
                shared=share.filter(user=request.user).exists()
        except:
            pass
        posts[st]=like,favourite,sharecount,shared,comment_count
    
    story=Story.objects.all()

    search=None
    lookingUsers=None
    myfollowing=None
    myfollower=None
    users={}
    search=request.GET.get('search')

    if search:
        lookingUsers=User.objects.filter(Q(first_name__contains=search) | Q(last_name__contains=search) | Q(username__contains=search))
    if request.GET.get('follower'):
        myfollower=Follow.objects.filter(following=request.user)
    if request.GET.get('following'):
        myfollowing=Follow.objects.filter(follower=request.user)     
    if lookingUsers:
        for user in lookingUsers:
            try:
               following=Follow.objects.get(following=user,follower=request.user)
               follow=True
            except:
                follow=False
            users[user,follow]=user,follow
    if myfollower:
        for f in myfollower:
            user=f.follower
            try:
               following=Follow.objects.get(following=user,follower=request.user)
               follow=True
            except:
                follow=False
            users[user,follow]=user,follow
    if myfollowing:
        for f in myfollowing:
            user=f.following
            try:
               following=Follow.objects.get(following=user,follower=request.user)
               follow=True
            except:
                follow=False
            users[user,follow]=user,follow                         
    context={
        'post_items':posts,
        'stories':story, 
        'suggestions':suggestfollow, 
        'followers':follower,
        'users' :users, 
    }
    return render(request, 'main/index.html',context)


def CreatePost(request):
    if request.method=="POST":
        fm=PostForm(request.POST,request.FILES)
        tag_obj=[]
        user=request.user
        #if fm.is_valid():
        
        captions=request.POST.get('caption')
        contents=request.FILES.get('content')
        if not captions:
            captions=None

        if captions is None and contents is None:
            messages.error(request, "Something went wrong")
        else:           
            taglist=re.findall(r"#(\w+)", captions)
            #taglist=list(tags.split(','))
            #mention
            allmentions=re.findall(r"@(\w+)", captions)
            mentions=list(dict.fromkeys(allmentions))
        
            for tag in taglist:
                t, created =Tag.objects.get_or_create(title=tag)
                tag_obj.append(t)
            
            p,created=Post.objects.get_or_create(user=user,caption=captions,content=contents)
            p.tag.set(tag_obj)
            p.save()

            for mention in mentions:
                try:           
                    muser=User.objects.get(username=mention)
                    notic=Notification(post=p,user=muser,sender=request.user,notification_type='5')
                    notic.save()
                except:
                    pass    
                    
            messages.success(request, "Posted successfully,You can see it on your profile")
    return HttpResponseRedirect('/')     



@login_required(login_url='/user/loginuser')
def PostDetails(request,id):
    post=Post.objects.get(id=id)
    liked=Likes.objects.filter(post=post,user=request.user).count()
    profile=Profile.objects.get(user=request.user)
    favourite=profile.favourite.filter(id=post.id).count()
    shared=False
    sharecount=0
    try:     
        scount=Post.objects.filter(share=id).count()
        if scount > 0:
            sharecount=scount
            shared=Post.objects.filter(share=id,user=request.user).exists()
        else:    
            shareid=post.share.id
            share=Post.objects.filter(share=shareid)  
            shared=share.filter(user=request.user).exists()
            sharecount=share.count()
    except:
        pass          
    comments=None
    fm=None
    parent=None
    comments=Comment.objects.filter(post=post,parent=None).order_by('-id')
    commentreply={}
    for comment in comments:
        reply=Comment.objects.filter(parent=comment).count()
        commentreply[comment]=reply    

    comment_id=request.POST.get('comment_id')
    try:
        replies=Comment.objects.filter(post=post,parent__isnull=False).order_by('-id')
    except:
        replies=None

    if request.method=="POST":
        fm=CommentForm(request.POST)
        if fm.is_valid():
            bd=fm.cleaned_data['body']
            allmentions=re.findall(r"@(\w+)", bd)
            mentions=list(dict.fromkeys(allmentions))
 

            if comment_id is None:           
                comment=fm.save(commit=False)
                comment.post=post
                comment.user=request.user
                comment.save()
                for mention in mentions:
                    try:        
                        muser=User.objects.get(username=mention)
                        if not muser==request.user:
                            notic=Notification(post=post,comment=comment,user=muser,sender=request.user,notification_type='5')
                            notic.save()
                        else:
                            pass    
                    except:
                        pass                

            else:
                parent=Comment.objects.get(id=comment_id)
                reply=fm.save(commit=False)
                reply.post=post
                reply.user=request.user
                reply.parent=parent
                reply.save()

                for mention in mentions:
                    try:        
                        muser=User.objects.get(username=mention)
                        if not muser==request.user:
                            notic=Notification(post=post,comment=reply,user=muser,sender=request.user,notification_type='5')
                            notic.save()
                        else:
                            pass    
                    except:
                        pass                


        return HttpResponseRedirect(reverse('postdetails',args=[id]))                 
    else:
        fm=CommentForm()

    recentlikes=Likes.objects.filter(user=request.user).order_by('-id')[:5]
    likedpeople=Likes.objects.filter(post=post)
    followers=Follow.objects.filter(follower=request.user)
    likesuser={}
    for likeuser in likedpeople:
        user=likeuser.user
        try:
           following=Follow.objects.get(following=user,follower=request.user)
           follow=True
        except:
            follow=False
        likesuser[user,follow]=user,follow

    from_user=Post.objects.filter(user=post.user).order_by('-id')[:3]
    stream =Stream.objects.filter(user=request.user).order_by('-id')[:4]
    context={
        'post':post,
        'liked':liked,
        'favourite':favourite,
        'form':fm,
        'comments':comments,
        'replies':replies,
        'commentreply':commentreply,
        'sharecount':sharecount,
        'shared':shared,
        'recentlikes':recentlikes,
        'likedpeople':likedpeople,
        'from_user':from_user,
        'stream':stream,
        'likesuser':likesuser

    }
    return render(request, 'main/post_details.html',context)



#share system


def PostShare(request,id):
    post=Post.objects.get(id=id)
    user=request.user
    caption=request.POST.get('caption')
    try:
      shared=Post.objects.get(user=user,caption=caption,share=post)
      shared.delete()
    except:
      shared=None 
    if not shared:  
        create=Post.objects.create(user=user,caption=caption)
        create.share=post
        create.save()      
    return HttpResponseRedirect(reverse('postdetails',args=[id]))   





def Like(request,id):
    post=Post.objects.get(id=id)
    current_likes=post.likes
    user=request.user
    liked=Likes.objects.filter(post=post,user=user).count()
    active=None
    if not liked:
        like=Likes.objects.create(post=post,user=user)
        like.save()
        current_likes=current_likes+1
      
    else:
        like=Likes.objects.filter(post=post,user=user)
        like.delete()
        current_likes=current_likes-1
        
     
    post.likes=current_likes
    post.save()
    active=None
    try:
        like.exists()
        active=None
    except:
        active='has-text-danger'

    data={
       'likes':current_likes,
       'active':active
    }
    return JsonResponse(data)




def Tags(request,slug):
    #tag=Tag.objects.get(slug=slug)
    realslug=slug
    slug=slug.lower()
    posts=Post.objects.filter(tag__slug=slug)
    return render(request,'main/tag.html',{'posts':posts,'slug':realslug})

def favourite(request,id):
    post=Post.objects.get(id=id)
    user=request.user
    profile=Profile.objects.get(user=user)
    if profile.favourite.filter(id=post.id).exists():
        profile.favourite.remove(post)
        save=False
    else:
        profile.favourite.add(post)   
        save=True 
      
    return JsonResponse({'save':save})



def CountNotification(request):
    count_notification=0
    if request.user.is_authenticated:
       count_notification=Notification.objects.filter(user=request.user,is_show=False).count()   
    return {'count_notification': count_notification}

 
def Notifications(request,pk=None):
    if pk:
       try:
            notify=Notification.objects.get(id=pk,user=request.user)
            notify.delete()
            return HttpResponseRedirect('/notifications')
       except:
           return HttpResponseRedirect('/notifications')
    else:
        user=request.user
        notific=Notification.objects.filter(user=user).order_by('-date')
        Notification.objects.filter(user=user,is_show=False).update(is_show=True)
    return render(request, 'main/notifications.html',{'notifications':notific})


def Construction(request):
    return render(request, 'main/construction.html')


def Newstory(request):
    if request.method=="POST":
       fm=StoryForm(request.POST,request.FILES)

       if fm.is_valid():
           story=fm.save(commit=False)
           story.user=request.user
           story.save()
    else:    
       fm=StoryForm()
    return render(request, 'main/newstory.html',{'form':fm})



def Test(request):
    tag=Tag.objects.values()
    return HttpResponse(tag) 