from django import forms
from django.contrib.auth.models import User
from .models import Profile

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '输入您的用户名'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '输入您的密码'})
    )

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords don't match")
        return password_confirm


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['real_name', 'profile_picture']


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['real_name', 'profile_picture']  # You can add more fields as needed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Correctly update widget attributes using the `update` method
        self.fields['real_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control-file'})

    # Optional: Customize form fields if needed, e.g., add validation
    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture and picture.size > 5 * 1024 * 1024:  # Max size 5MB
            raise forms.ValidationError("Image file too large. Max size is 5MB.")
        return picture