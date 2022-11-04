import streamlit as st
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2
from . import session_state
from . import data_handler


default_ttl = 60


async def get_authorization_url(client, redirect_uri):
    authorization_url = await client.get_authorization_url(redirect_uri, scope=["profile", "email"])
    return authorization_url


async def get_access_token(client, redirect_uri, code):
    token = await client.get_access_token(code, redirect_uri)
    return token


async def get_email(client, token):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email


def refresh_token(client, token):
    token = client.refresh_token(token["refresh_token"])
    return token


def nav_to(url):
    nav_script = """
        <meta http-equiv="refresh" content="0; url='%s'">
    """ % (url)
    st.write(nav_script, unsafe_allow_html=True)


def create_google_client():
    google_client = GoogleOAuth2(st.secrets.google['CLIENT_ID'], st.secrets.google['CLIENT_SECRET'])
    redirect_uri = st.secrets.google['REDIRECT_URI']
    return google_client, redirect_uri


def sign_in(provider):
    if provider == 'google':
        client, redirect_uri = create_google_client()
        url = asyncio.run(get_authorization_url(client, redirect_uri))
        nav_to(url)
    elif provider == 'facebook':
        st.warning('Not yet implemented')
    elif provider == 'linkedin':
        st.warning('Not yet implemented')


def check_provider(query_params):
    scope = query_params['scope'][0]
    code = query_params['code']
    if 'www.googleapis.com' in scope:
        client, redirect_uri = create_google_client()
        return code, client, redirect_uri


def check_sign_in(query_params):
    if not query_params:
        return False
    elif session_state.get_session_state('access_token'):
        st.write("access token exists")
    else:
        try:
            code, client, redirect_uri = check_provider(query_params)
            token = asyncio.run(get_access_token(client, redirect_uri, code))
            session_state.set_session_state('access_token', token)
            user_id, user_email = asyncio.run(get_email(client, token['access_token']))
            session_state.set_session_state('user_email', user_email)
            auth_table = get_auth_table()
            if user_email in auth_table:
                return True
        except:
            return False


@st.cache(ttl=default_ttl)
def get_auth_table():
    auth_table = data_handler.get_private_file('pseudo_db.txt')
    return auth_table
