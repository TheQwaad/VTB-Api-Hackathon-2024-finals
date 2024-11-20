from django.urls import path

from base.views import views, story_auth_views, nft_auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("test", views.TestView.as_view(), name="test"),

    # story auth flow
    path("register", views.RegisterView.as_view(), name="auth.register"),
    path("story/verify_app/<int:user_id>", story_auth_views.VerifyAppView.as_view(), name="auth.verify_app"),
    path("story/login", story_auth_views.LoginView.as_view(), name="auth.login"),
    path("story/login_confirm/<int:user_id>", story_auth_views.LoginConfirmView.as_view(), name="auth.login_confirm"),
    path("story/story/show", story_auth_views.GetStoryView.as_view(), name="story.show"),
    path("story/logout", story_auth_views.LogoutView.as_view(), name="auth.logout"),

    # NFT auth flow
    path("nft/verify_app/<int:user_id>", nft_auth_views.VerifyRegisterView.as_view(), name="nft_auth.verify_app"),
    path("nft/login", nft_auth_views.LoginView.as_view(), name="nft_auth.login"),
    path("nft/logout", nft_auth_views.LogoutView.as_view(), name="nft_auth.logout"),
    path('nft/complete-login/', nft_auth_views.complete_login, name='complete_login'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)