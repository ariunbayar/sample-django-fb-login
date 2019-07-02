from django.urls import path
import user.views
import secure.views


urlpatterns = [

    path('', user.views.profile, name="user-profile"),

    path('login', secure.views.login, name="login"),
    path('redirect-to-fb-login', secure.views.redirect_to_fb_login, name="redirect_to_fb_login"),
    path('check-fb-login', secure.views.check_fb_login, name="check_fb_login"),
    path('logout', secure.views.logout, name="logout"),

    path('deauth-facebook', secure.views.deauth_facebook),
]
