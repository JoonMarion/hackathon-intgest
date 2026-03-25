from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from . import views
from .forms import EmailOrUsernameAuthenticationForm

app_name = "accounts_http"

urlpatterns = [
    path("", LoginView.as_view(template_name="accounts/pages/login.html", authentication_form=EmailOrUsernameAuthenticationForm), name="index"),
    path("login/", LoginView.as_view(template_name="accounts/pages/login.html", authentication_form=EmailOrUsernameAuthenticationForm), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("perfil/", views.ProfileDetailView.as_view(), name="profile"),
    path("perfil/editar/", views.ProfileEditView.as_view(), name="profile_edit"),
    path("perfil/senha/", views.ProfilePasswordChangeView.as_view(), name="password_change"),
    path("logout/", LogoutView.as_view(next_page="accounts_http:login"), name="logout"),
]
