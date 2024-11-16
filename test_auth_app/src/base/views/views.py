from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.views import APIView
from django.shortcuts import render
from base.models import StoryAuthUser


class IndexView(APIView):
    def get(self, request: Request):
        users = StoryAuthUser.objects.all()
        return render(request, 'index.html', {'users': users})


class ProfileView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        return render(request, 'profile.html')
