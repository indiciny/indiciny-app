import streamlit as st
from . import view_sidebar
from . import view_data
from . import view_method
from . import authentication


def init_login_view():
    view_sidebar.draw_signin_sidebar()
    st.title('Please sign in to use indiciny for free!')

    google_button = st.button('Sign in with Google')
    #facebook_button = st.button('Sign in with Facebook')
    #linkedin_button = st.button('Sign in with LinkedIn')

    if google_button:
        authentication.sign_in('google')
    #elif facebook_button:
    #    authentication.sign_in('facebook')
    #elif linkedin_button:
    #    authentication.sign_in('linkedin')


def init_app_view():
    st.title('indiciny Data Analytics Platform')

    view_data.draw_source()
    view_data.draw_source_view()
    st.write('___')
    # Analysis part
    view_method.draw_method()
    view_method.draw_method_view()

    view_sidebar.draw_sidebar()
    view_sidebar.draw_counter()
