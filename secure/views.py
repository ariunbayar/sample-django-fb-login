import uuid

from django.conf import settings
from django.http import HttpResponse, Http404
from django.http import QueryDict
from django.shortcuts import render, reverse, redirect


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

    # Check if login succeeded
    code = request.GET.get('code')
    if code:  # Login success and code acquired
        return HttpResponse('TODO proceed fb login')
    else:
        q = QueryDict(mutable=True)
        q['error'] = request.GET.get('error_description', 'Login failed')

        return redirect(reverse('login') + '?' + q.urlencode(safe='/'))


def logout(request):

    return HttpResponse('TODO logout_fb')
