from base64 import b64decode
import hashlib
import hmac
import json
import uuid

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.http import QueryDict
from django.shortcuts import render, reverse, redirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from main.fbclient import FBClient


def login(request):

    context = {
            'login_error': request.GET.get('error'),
        }

    return render(request, 'secure/login.html', context)


def redirect_to_fb_login(request):

    redirect_uri = request.build_absolute_uri(reverse('check_fb_login'))

    login_state = uuid.uuid4().hex
    request.session['login_state'] = login_state

    fbclient = FBClient(settings.FB_APP)
    fb_login_dialog_url = fbclient.get_login_url(redirect_uri, login_state)

    return redirect(fb_login_dialog_url)


def check_fb_login(request):

    # Validate state
    state = request.GET.get('login_state')
    if request.session.get('login_state') == state:
        raise Http404('Error: login state mismatch')

    def _create_account(User, user_info, access_token):
        user = User()
        user.username = 'facebook_user_' + user_info.get('id')
        user.first_name = user_info.get('first_name')
        user.last_name = user_info.get('last_name')
        user.fb_user_id = user_info.get('id')
        user.is_active = True
        user.access_token = access_token
        user.save()
        return user

    try:

        code = request.GET.get('code')
        if not code:
            message = request.GET.get('error_description', 'Login failed')
            raise Exception(message)

        fbclient = FBClient(settings.FB_APP)

        redirect_uri = request.build_absolute_uri(reverse('check_fb_login'))

        token = fbclient.fetch_access_token(code, redirect_uri)
        if 'error' in token:
            raise Exception(token['error'].get('message'))

        # Login success

        user_info = fbclient.fetch_user_info()
        if 'error' in user_info:
            raise Exception(user_info['error'].get('message'))

        User = auth.get_user_model()
        try:
            user = User.objects.get(fb_user_id=user_info.get('id'))
        except User.DoesNotExist:
            user = _create_account(User, user_info, token.get('access_token'))

        auth.login(request, user)

        return redirect('user-profile')

    except Exception as error:
        q = QueryDict(mutable=True)
        q['error'] = str(error)

        return redirect(reverse('login') + '?' + q.urlencode(safe='/'))


@login_required
def logout(request):
    auth.logout(request)
    return redirect('login')


@csrf_exempt
def deauth_facebook(request):

    # Ref: https://developers.facebook.com/docs/games/gamesonfacebook/login#parsingsr

    def _base64_url_decode(data):
        data = data.replace('-', '+').replace('_', '/')
        data += '=' * (4 - len(data) % 4)
        return b64decode(data)

    signed_request = request.POST.get('signed_request')
    encoded_sig, payload = signed_request.split('.', 1)

    secret = settings.FB_APP['secret']

    # decode data
    sig = _base64_url_decode(encoded_sig)
    data = json.loads(_base64_url_decode(payload))

    if data.get('algorithm') != 'HMAC-SHA256':
        raise Exception('undefined hash: ' + data.get('algorithm'))

    expected_sig = hmac.new(secret.encode(), msg=payload.encode(), digestmod=hashlib.sha256).digest()
    if sig != expected_sig:
        raise Http404

    user = get_object_or_404(auth.get_user_model(), fb_user_id=data.get('user_id'))
    user.is_active = False
    user.save()

    return HttpResponse('Success')
