from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    duplicated_username_message = "Já existe uma conta com este nome de usuário."
    duplicated_email_message = "Já existe uma conta com este e-mail."

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"data-e2e-selector": "accounts-register-username-input"})
        self.fields["email"].widget.attrs.update({"data-e2e-selector": "accounts-register-email-input"})
        self.fields["password1"].widget.attrs.update({"data-e2e-selector": "accounts-register-password1-input"})
        self.fields["password2"].widget.attrs.update({"data-e2e-selector": "accounts-register-password2-input"})

    def clean_username(self):
        username = self.cleaned_data["username"]
        User = get_user_model()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(self.duplicated_username_message)
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(self.duplicated_email_message)
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    duplicated_username_message = "Já existe uma conta com este nome de usuário."
    duplicated_email_message = "Já existe uma conta com este e-mail."

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"data-e2e-selector": "accounts-profile-edit-username-input"})
        self.fields["email"].widget.attrs.update({"data-e2e-selector": "accounts-profile-edit-email-input"})
        self.fields["first_name"].widget.attrs.update({"data-e2e-selector": "accounts-profile-edit-first-name-input"})
        self.fields["last_name"].widget.attrs.update({"data-e2e-selector": "accounts-profile-edit-last-name-input"})

    def clean_username(self):
        username = self.cleaned_data["username"]
        User = get_user_model()
        queryset = User.objects.filter(username__iexact=username)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError(self.duplicated_username_message)
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        User = get_user_model()
        queryset = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError(self.duplicated_email_message)
        return email


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = AuthenticationForm.declared_fields["username"].__class__(
        label="Usuário ou e-mail",
        max_length=254,
        widget=forms.TextInput(attrs={"autofocus": True, "data-e2e-selector": "accounts-login-username-input"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password"].widget.attrs.update({"data-e2e-selector": "accounts-login-password-input"})

    def clean(self):
        username = self.cleaned_data.get("username")
        if username and "@" in username:
            User = get_user_model()
            user = User.objects.filter(email__iexact=username).first()
            if user:
                self.cleaned_data["username"] = user.username
        return super().clean()
