from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("/profile", views.ProfileView.as_view(), name="profile"),
    path("/register", views.RegisterView.as_view(), name="register"),
    path("/login", views.LoginView.as_view(), name="login"),
    path("/login_2fa", views.Login2FAView.as_view(), name="login_2fa"),
    path("/logout", views.LogoutView.as_view(), name="logout"),
]