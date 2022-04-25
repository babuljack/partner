from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm

user=get_user_model()


class DateInput(forms.DateInput):
    input_type = 'date'

class SignUpForm(UserCreationForm):
    CHOICES = [('1','Male'),('2','Female'),('3','Other')]
    gender=forms.CharField(widget=forms.RadioSelect(choices=CHOICES))
    password1=forms.CharField(label='New Password',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'New Password'}))
    password2=forms.CharField(label='Confirm Password',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'}))
    class Meta:
        model=user
        fields=['first_name','last_name','username','email','db','gender']
        widgets={
            'first_name':forms.TextInput(attrs={'class':'form-control','placeholder':'First Name'}),
            'last_name':forms.TextInput(attrs={'class':'form-control','placeholder':'Last Name'}),
            'username':forms.TextInput(attrs={'class':'form-control','placeholder':'User Name'}),
            'db':DateInput(attrs={'class':'form-control'}),
            'email':forms.EmailInput(attrs={'class':'form-control','placeholder':'Type Email'}),
    
            
        }

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model=user
        fields=['first_name','last_name','email']
        widgets={
            'first_name':forms.TextInput(attrs={'class':'form-control'}),
            'last_name':forms.TextInput(attrs={'class':'form-control'}),
            'email':forms.EmailInput(attrs={'class':'form-control'})
            }


class LoginForm(AuthenticationForm):
    username=forms.CharField(widget=forms.TextInput(attrs={'placeholder':'Username Or Email'}))
    password=forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Type Password'}))
    class Meta:
        model=user
        



