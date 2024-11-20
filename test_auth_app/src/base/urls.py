from django.urls import path

from base.views import views, story_auth_views, nft_auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # common views
    path("", views.IndexView.as_view(), name="index"),
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("test", views.TestView.as_view(), name="test"),
    path("register", views.RegisterView.as_view(), name="auth.register"),
    path("login", views.LoginView.as_view(), name="auth.login"),
    path("logout", views.LogoutView.as_view(), name="auth.logout"),

    # story auth flow
    path("story/verify_app/<int:user_id>", story_auth_views.VerifyAppView.as_view(), name="auth.verify_app"),
    path("story/login_confirm/<int:user_id>", story_auth_views.LoginConfirmView.as_view(), name="auth.login_confirm"),
    path("story/story/show", story_auth_views.GetStoryView.as_view(), name="story.show"),

    # NFT auth flow
    path("nft/verify_app/<int:user_id>", nft_auth_views.VerifyRegisterView.as_view(), name="nft_auth.verify_app"),
    path('nft/complete-login/', nft_auth_views.complete_login, name='complete_login'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)