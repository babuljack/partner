from django.db import models
from django.utils.text import slugify
import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save,post_delete
from Account.models import User

# Create your models here

class Tag(models.Model):
    title = models.CharField(max_length=75, verbose_name='Tag')
    slug = models.SlugField(null=False, unique=True)

    def __str__(self):
        return self.title

    def save(self,*args,**kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)    

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'post/{0}/{1}'.format(instance.user.username, filename)

def story_path(instance,filename):
    return 'Story/{0}/{1}'.format(instance.user.username, filename)



class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    caption=models.CharField(max_length=120,blank=False,null=False)
    content=models.FileField(upload_to=user_directory_path,null=True)
    tag=models.ManyToManyField(Tag,related_name='tags')
    likes=models.PositiveIntegerField(default=0)
    share=models.ForeignKey('self', on_delete=models.CASCADE,null=True,blank=True)
    date=models.DateTimeField(auto_now_add=True)

    def post_share(sender,instance,*args,**kwargs):
        if instance.share is not None:
            share=instance
            post=share.share
            sender=share.user
            user=post.user
            try:
               notic=Notification.objects.get(post=post,sender=sender,user=user,notification_type='3')
            except:
               notic=None
            if notic:
                pass
            else:
                notify=Notification(post=post,sender=sender,user=user,notification_type='3')
                notify.save()            
        else:
            pass

    def post_unshare(sender, instance, *args, **kwargs):
        try:
            if instance.share is not None:
                share=instance
                post=share.share.post
                sender=share.user
                user=post.user
                try:
                    notic=Notification.objects.get(post=post,sender=sender,user=user,notification_type='3')
                    notic.delete()
                except:
                    pass    
        except:
            pass


    def __str__(self):
      
        if self.share is None:   
           return f'{self.caption}-{self.id}'
        else:
           return f'{self.share.caption} shared by {self.user}'   

class Likes(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE ,related_name='post_like') 
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name='post_user')
    
    def user_like_post(sender, instance, *args, **kwargs):
        like=instance
        post=like.post
        sender=like.user
        user=post.user
        if user==sender:
            pass
        else:
            try:
                notic=Notification.objects.get(post=post,sender=sender,user=user,notification_type='1')
            except:
                notic=None
            if notic:
                pass
            else:
                notify=Notification(post=post,sender=sender,user=user,notification_type='1')
                notify.save()

    def user_unlike_post(sender, instance, *args, **kwargs):
        like=instance
        post=like.post
        sender=like.user
        user=post.user
        try:
            notic=Notification.objects.get(post=post,sender=sender,user=user,notification_type='1')
            notic.delete()
        except:
            pass    

class Follow(models.Model):
    following=models.ForeignKey(User, on_delete=models.CASCADE,related_name='following')
    follower=models.ForeignKey(User, on_delete=models.CASCADE,related_name='follower')

    def user_follow(sender, instance, *args, **kwargs):
        follow=instance
        following=follow.following
        follower=follow.follower
        try:
           notic=Notification.objects.get(sender=follower,user=following,notification_type=4)
        except:
           notic=None
        if notic:
            pass
        else:
            notify=Notification(sender=follower,user=following,notification_type=4)
            notify.save()

    def user_unfollow(sender, instance, *args, **kwargs):
        follow=instance
        following=follow.following
        follower=follow.follower
        try:
           notic=Notification.objects.get(sender=follower,user=following,notification_type=4)
           notic.delete()
        except:
           pass   

    def __str__(self):
        return f'{self.follower} followd {self.following}' 

class Stream(models.Model):
    following=models.ForeignKey(User, on_delete=models.CASCADE,related_name='stream_following')
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    user=models.ManyToManyField(User)
    date=models.DateTimeField(null=True)

    @receiver(post_save,sender=Post)
    def add_post(sender, instance, *args, **kwargs):
        post=instance
        user=post.user
        date=post.date
        followers=Follow.objects.filter(following=user)
        follower_obj=[]
        for follow in followers:
            follower_obj.append(follow.follower)
        if follower_obj:    
            try:
                s,stream=Stream.objects.get_or_create(following=user,post=post,date=date)
                s.user.set(follower_obj)
                s.save()
            except:
                stream=Stream.objects.filter(following=user,date=date,post=post,user__in=follower_obj)
                for st in stream:
                    st.save()    
            
           

    def __str__(self):
        return f'created by {self.post.user}'


class Comment(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE)
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    body=models.CharField(max_length=200)
    parent=models.ForeignKey('self', on_delete=models.CASCADE,null=True,blank=True)
    time=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.parent is None:
            status=f'Commented by {self.user} on {self.post.caption}'
        else:
            status=f'Replied by {self.user} on {self.post.caption}'
        return status


    def totalcomments(post):
        count=Comment.objects.filter(post=post).count()
        return count

    def user_comment(sender, instance, *args, **kwargs):
        if instance.parent is None:
            comment=instance
            post=comment.post
            sender=comment.user
            user=post.user
            text=comment.body
            if sender == user:
                pass
            else:
                try:
                    notic=Notification.objects.get(post=post,sender=sender,text=text,user=user,notification_type='2')
                except:
                    notic=None
                if notic:
                    pass
                else:
                    notify=Notification(post=post,sender=sender,text=text,user=user,notification_type='2')
                    notify.save()
        else:
            comment=instance
            post=comment.post
            sender=comment.user
            user=post.user
            reply=comment.parent
            if sender == user:
                pass
            else:
                try:
                    notic=Notification.objects.get(post=post,sender=sender,comment=reply,user=user,notification_type='2')
                except:
                    notic=None
                if notic:
                    pass
                else:
                    notify=Notification(post=post,sender=sender,comment=reply,user=user,notification_type='2')
                    notify.save()
  
    def user_uncomment(sender, instance, *args, **kwargs):
        comment=instance
        post=comment.post
        sender=comment.user
        user=post.user
        text=comment.body
        try:
            try:
                notic=Notification.objects.get(post=post,sender=sender,text=text,user=user,notification_type='2')
                notic.delete()
            except:
                notify=Notification(post=post,sender=sender,comment=reply,user=user,notification_type='2')
                notify.delete()   
        except:
            pass    


class Story(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    content=models.FileField(upload_to=story_path)
    text=models.CharField(max_length=120)
    time=models.DateTimeField(auto_now_add=True)
    expire=models.BooleanField(default=False)

















notification_type=(
(1,'like'),
(2,'comment'),
(3,'share'),
(4,'follow'),
(5,'mention')

)

class Notification(models.Model):
    post=models.ForeignKey(Post, on_delete=models.CASCADE,null=True,blank=True)
    sender=models.ForeignKey(User, on_delete=models.CASCADE,related_name='post_senders')
    user=models.ForeignKey(User, on_delete=models.CASCADE,related_name='post_users')
    notification_type=models.CharField(choices=notification_type,max_length=20)
    text=models.CharField(max_length=120,null=False,blank=False)
    comment=models.ForeignKey(Comment,on_delete=models.CASCADE, null=True,blank=False)
    date=models.DateTimeField(auto_now_add=True)
    is_show=models.BooleanField(default=False)   



#Likes
post_save.connect(Likes.user_like_post, sender=Likes)
post_delete.connect(Likes.user_unlike_post, sender=Likes)

#follow
post_save.connect(Follow.user_follow, sender=Follow)
post_delete.connect(Follow.user_unfollow, sender=Follow)

#comment
post_save.connect(Comment.user_comment, sender=Comment)
post_delete.connect(Comment.user_uncomment, sender=Comment)
#share
post_save.connect(Post.post_share, sender=Post)
post_delete.connect(Post.post_unshare, sender=Post)
#mention

