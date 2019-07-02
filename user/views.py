from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.conf import settings
from main.fbclient import FBClient


@login_required
def profile(request):

    fbclient = FBClient(settings.FB_APP, request.user.access_token)
    user_info = fbclient.fetch_user_info()

    context = {
            'name': user_info.get('name'),
            'picture': user_info.get('picture').get('data'),
        }

    return render(request, 'user/profile.html', context)
