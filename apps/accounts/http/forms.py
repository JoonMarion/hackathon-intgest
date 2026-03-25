from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = AuthenticationForm.declared_fields["username"].__class__(
        label="Usuário ou e-mail",
        max_length=254,
        widget=forms.TextInput(attrs={"autofocus": True}),
    )

    def clean(self):
        username = self.cleaned_data.get("username")
        if username and "@" in username:
            User = get_user_model()
            user = User.objects.filter(email__iexact=username).first()
            if user:
                self.cleaned_data["username"] = user.username
        return super().clean()
