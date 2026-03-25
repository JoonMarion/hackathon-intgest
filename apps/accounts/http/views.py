from django.contrib import messages
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import RegisterForm, UserProfileForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/pages/register.html"
    success_url = reverse_lazy("accounts_http:login")


class ProfileDetailView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/pages/profile_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_user"] = self.request.user
        return context


class ProfileEditView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = UserProfileForm
    template_name = "accounts/pages/profile_edit.html"
    success_url = reverse_lazy("accounts_http:profile")
    success_message = "Dados atualizados com sucesso."

    def get_object(self, queryset=None):
        return self.request.user


class ProfilePasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = "accounts/pages/password_change.html"
    success_url = reverse_lazy("accounts_http:profile")

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["old_password"].widget.attrs.update({"data-e2e-selector": "accounts-password-change-old-password-input"})
        form.fields["new_password1"].widget.attrs.update({"data-e2e-selector": "accounts-password-change-new-password1-input"})
        form.fields["new_password2"].widget.attrs.update({"data-e2e-selector": "accounts-password-change-new-password2-input"})
        return form

    def form_valid(self, form):
        messages.success(self.request, "Senha alterada com sucesso.")
        return super().form_valid(form)
