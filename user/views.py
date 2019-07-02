from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def profile(request):

    context = {}

    return render(request, 'user/profile.html', context)
