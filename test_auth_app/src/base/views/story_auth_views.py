from rest_framework.request import Request, HttpRequest
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import login
from django.shortcuts import render, redirect
from base.models import *
from base.serializers.model_serializers import VerifyMobileAppUserSerializer, MobileSerializer
from rest_framework.serializers import ValidationError
from base.services.qr_service import QrService
from django.views import View


class VerifyAppView(APIView):
    def get(self, request: Request, user_id: int):
        user: BaseUser = BaseUser.objects.get_or_fail(id=user_id)
        if not user.is_story_auth_enabled:
            raise ValidationError('Cannot verify app for user with no story auth enabled')
        img_html = QrService.generate_mobile_verify_qr(user)
        return render(request, 'story_auth/verify_app.html', {'img': img_html, 'user_id': user_id})

    def post(self, request: Request, user_id: int):
        try:
            user: BaseUser = BaseUser.objects.get_or_fail(id=user_id)
            serializer = VerifyMobileAppUserSerializer(user, data=request.data)
            user = serializer.verify_mobile_app()
            user.regenerate_jwt()
            return Response(data={'jwt': user.jwt_token})
        except ValidationError as e:
            return Response(data={'error': e.detail})


class IsAppVerifiedView(APIView):
    def get(self, request: Request, user_id: int):
        user: BaseUser = BaseUser.objects.get_or_fail(id=user_id)
        return Response(data={
            'verified': user.get_story_auth_method().is_mobile_verified(),
            'redirect': user.get_register_redirect_str()
        })


class LoginConfirmView(View):
    async def get(self, request: Request, user_id: int):
        from asgiref.sync import sync_to_async
        user: BaseUser = await sync_to_async(BaseUser.objects.get_or_fail)(id=user_id)
        if await sync_to_async(user.get_story_auth_method)() is None:
            raise ValidationError('Cannot check story for user with no story')
        story = await sync_to_async(user.story_set.get)()
        options = (await sync_to_async(story.get_correct_options)())[:1] + await sync_to_async(story.get_incorrect_options)()
        return await sync_to_async(render)(request, "story_auth/login_confirm.html", {
            'options': options,
            'user_id': user.id
        })

    async def post(self, request: Request, user_id: int):
        from asgiref.sync import sync_to_async

        chosen_option = await sync_to_async(request.POST.get)('chosen_option')
        if chosen_option is None:
            raise ValidationError('You must choose story option')

        user: BaseUser = await sync_to_async(BaseUser.objects.get_or_fail)(id=user_id)
        if await sync_to_async(user.get_story_auth_method)() is None:
            raise ValidationError('Cannot check story for user with no story')
        story = await sync_to_async(user.story_set.get)()
        if story is None or await sync_to_async(story.is_expired)():
            raise ValidationError('Your story verification time expired')
        if chosen_option not in await sync_to_async(story.get_correct_options)():
            raise ValidationError('You chose incorrect option')

        if await sync_to_async(user.get_nft_auth_method)() is not None:
            from base.views.views import LoginView
            return LoginView().post(Request(HttpRequest()), user_id)

        await sync_to_async(login)(request, user)
        return await sync_to_async(redirect)('profile')


class GetStoryView(APIView):
    def post(self, request: Request):
        try:
            serializer = MobileSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = StoryAuthMethod.get_by_mobile_credentials(
                serializer.validated_data['jwt_token'],
                serializer.validated_data['mobile_identifier']
            )
            story = Story.objects.filter(user_id=user.id, expires_at__gte=now()).first()
            if story is None:
                raise ValidationError('All your stories expired')

            user.regenerate_jwt()
            return Response(data={
                'jwt': user.jwt_token,
                'story': story.story
            })
        except ValidationError as e:
            return Response(data={'error': e.detail})
