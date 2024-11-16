from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("register", views.RegisterView.as_view(), name="auth.register"),
    path("verify_app/<int:user_id>", views.VerifyAppView.as_view(), name="auth.verify_app"),
    path("login", views.LoginView.as_view(), name="auth.login"),
    path("logout", views.LogoutView.as_view(), name="auth.logout"),
]