from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Username or email"

    def clean(self):
        identifier = self.cleaned_data.get("username", "").strip()
        if "@" in identifier:
            user = User.objects.filter(email__iexact=identifier).first()
            if user:
                self.cleaned_data["username"] = user.get_username()
        return super().clean()


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=254)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account already uses this email address.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
