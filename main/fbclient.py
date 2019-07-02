import requests


class FBClient:

    def __init__(self, app_config, access_token=None):
        self.app_id = app_config['id']
        self.app_secret = app_config['secret']
        self.scope = app_config['scope']
        self.access_token = access_token

    def get_login_url(self, redirect_uri, login_state):

        login_url = (
                'https://www.facebook.com/v3.3/dialog/oauth?'
                'client_id={app_id}'
                '&redirect_uri={redirect_uri}'
                '&state={state_param}'
                '&scope={scope}'
            ).format(
                app_id=self.app_id,
                redirect_uri=redirect_uri,
                state_param=login_state,
                scope=self.scope,
            )
        return login_url

    def fetch_access_token(self, code, redirect_uri):

        # According to FB:
        # redirect_uri - This argument is required and must be the same as the original
        #                request_uri that you used when starting the OAuth login process.

        url = (
               'https://graph.facebook.com/v3.3/oauth/access_token?'
               'client_id={app_id}'
               '&redirect_uri={redirect_uri}'
               '&client_secret={app_secret}'
               '&code={code}'
            ).format(
                app_id=self.app_id,
                redirect_uri=redirect_uri,
                app_secret=self.app_secret,
                code=code,
            )

        rsp = requests.get(url)
        rsp_data = rsp.json()

        if 'access_token' in rsp_data:
            self.access_token = rsp_data['access_token']
        return rsp_data

    def fetch_user_info(self):

        url = (
               'https://graph.facebook.com/me?'
               'fields=id,name,first_name,last_name,picture'
               '&access_token={access_token}'
            ).format(
                access_token=self.access_token,
            )

        rsp = requests.get(url)
        return rsp.json()
