import uuid


from django.conf import settings
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.http import QueryDict
from django.shortcuts import render, reverse, redirect
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

    # Build Facebook login url
    fb_login_dialog_url = (
            'https://www.facebook.com/v3.3/dialog/oauth?'
            'client_id={app_id}'
            '&redirect_uri={redirect_uri}'
            '&state={state_param}'
            '&scope={scope}'
        ).format(
            app_id=settings.FB_APP['id'],
            redirect_uri=redirect_uri,
            state_param=login_state,
            scope=settings.FB_APP['scope'],
        )

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
