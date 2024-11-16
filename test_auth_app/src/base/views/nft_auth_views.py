from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from base.models import StoryAuthUser
from base.serializers.model_serializers import StoryAuthUserSerializer, VerifyMobileAppUserSerializer, LoginUserSerializer, MobileSerializer
from rest_framework.serializers import ValidationError
from base.services.qr_service import QrService


class RegisterView(APIView):
    def get(self, request: Request):
        return render(request, 'story_auth/register.html')

    def post(self, request: Request):
        user_serializer = StoryAuthUserSerializer(data=request.data)
        user_serializer.is_valid(raise_exception=True)
        user: StoryAuthUser = user_serializer.save()
        return redirect("auth.verify_app", user_id=user.id)


class VerifyAppView(APIView):
    def get(self, request: Request, user_id: int):
        user: StoryAuthUser = StoryAuthUser.objects.get_or_fail(id=user_id)
        img_html = QrService.generate_mobile_verify_qr(user)
        return render(request, 'story_auth/verify_app.html', {'img': img_html})

    def post(self, request: Request, user_id: int):
        try:
            user: StoryAuthUser = StoryAuthUser.objects.get_or_fail(id=user_id)
            serializer = VerifyMobileAppUserSerializer(user, data=request.data)
            user = serializer.verify_mobile_app()
            user.regenerate_jwt()
            return Response(data={'jwt': user.jwt_token})
        except ValidationError as e:
            return Response(data={'error': e.__str__()})


class LoginView(APIView):
    def get(self, request: Request):
        return render(request, "story_auth/login.html")

    def post(self, request: Request):
        serializer = LoginUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = StoryAuthUser.authenticate(serializer.validated_data['username'], serializer.validated_data['password'])
        if not user.is_mobile_verified():
            return redirect("auth.verify_app", user_id=user.id)
        user.regenerate_story()
        return redirect('auth.login_confirm', user_id=user.id)


class LoginConfirmView(APIView):
    def get(self, request: Request, user_id: int):
        user: StoryAuthUser = StoryAuthUser.objects.get_or_fail(id=user_id)
        story = user.story_set.get()
        return render(request, "story_auth/login_confirm.html", {
            'options': story.get_correct_options() + story.get_incorrect_options(),
            'user_id': user.id
        })

    def post(self, request: Request, user_id: int):
        chosen_option = request.POST.get('chosen_option')
        if chosen_option is None:
            raise ValidationError('You must choose story option')

        user: StoryAuthUser = StoryAuthUser.objects.get_or_fail(id=user_id)
        story = user.story_set.get()
        if story is None or story.is_expired():
            raise ValidationError('Your story verification time expired')
        if chosen_option not in story.get_correct_options():
            raise ValidationError('You chose incorrect option')

        login(request, user)
        return redirect('profile')


class GetStoryView(APIView):
    def post(self, request: Request):
        try:
            serializer = MobileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = StoryAuthUser.get_by_mobile_credentials(
                serializer.validated_data['jwt_token'],
                serializer.validated_data['mobile_identifier']
            )
            story = user.story_set.get()
            if story is None or story.is_expired():
                raise ValidationError('All your stories expired')

            user.regenerate_jwt()
            return Response(data={
                'jwt': user.jwt_token,
                'story': story.story
            })
        except ValidationError as e:
            return Response(data={'error': e.__str__()})


class LogoutView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        logout(request)
        return redirect("index")