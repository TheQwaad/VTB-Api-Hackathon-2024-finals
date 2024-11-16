from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from django.shortcuts import render
from base.models import StoryAuthUser, NftAuthUser


class IndexView(APIView):
    def get(self, request: Request):
        story_users = StoryAuthUser.objects.all()
        nft_users = NftAuthUser.objects.all()
        return render(request, 'index.html', {
            'story_users': story_users,
            'nft_users': nft_users
        })


class ProfileView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        return render(request, 'profile.html')
