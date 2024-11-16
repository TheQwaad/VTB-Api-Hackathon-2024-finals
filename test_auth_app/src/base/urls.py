from django.urls import path

from base.views import views, story_auth_views, nft_auth_views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("profile", views.ProfileView.as_view(), name="profile"),

    # story auth flow
    path("story/register", story_auth_views.RegisterView.as_view(), name="auth.register"),
    path("story/verify_app/<int:user_id>", story_auth_views.VerifyAppView.as_view(), name="auth.verify_app"),
    path("story/login", story_auth_views.LoginView.as_view(), name="auth.login"),
    path("story/login_confirm/<int:user_id>", story_auth_views.LoginConfirmView.as_view(), name="auth.login_confirm"),
    path("story/story/show", story_auth_views.GetStoryView.as_view(), name="story.show"),
    path("story/logout", story_auth_views.LogoutView.as_view(), name="auth.logout"),

    # NFT auth flow
    path("nft/register", nft_auth_views.RegisterView.as_view(), name="nft_auth.register"),
    path("nft/verify_app/<int:user_id>", nft_auth_views.VerifyRegisterView.as_view(), name="nft_auth.verify_app"),
    path("nft/login", nft_auth_views.LoginView.as_view(), name="nft_auth.login"),
    path("nft/logout", nft_auth_views.LogoutView.as_view(), name="nft_auth.logout"),
]