from flask import url_for, redirect, request
from app import app
from rauth import OAuth2Service


class FacebookOAuth(object):
    def __init__(self):
        credentials = app.config['OAUTH']['facebook']
        self.client_id = credentials['id']
        self.client_secret = credentials['secret']
        self.service = OAuth2Service(
                    name='facebook',
                    client_id=self.client_id,
                    client_secret=self.client_secret,
                    authorize_url='https://graph.facebook.com/oauth/authorize',
                    access_token_url='https://graph.facebook.com/oauth/access_token',
                    base_url='https://graph.facebook.com/')

    def authorize(self):
        return redirect(self.service.get_authorize_url(scope='email',
                                                    response_type='code',
                                                    redirect_uri=self.get_callback_url())
                        )

    def callback(self):
        if 'code' not in request.args:
            return None
        oauth_session = self.service.get_auth_session(data={
            'code': request.args['code'],
            'grant_type': 'authorization_code',
            'redirect_uri': self.get_callback_url()
        })
        me = oauth_session.get('me').json()
        return('facebook$' + me['id'],
                me.get('email').split('@')[0],
                me.get('email'))

    def get_callback_url(self):
        return url_for('oauth_callback_facebook', provider='facebook',
                       _external=True)
