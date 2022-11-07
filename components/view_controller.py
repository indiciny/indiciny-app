import streamlit as st
from . import view_sidebar
from . import view_data
from . import view_method
from . import authentication


def init_always():
    hide_decoration_bar_style = '''
        <style>
            header {visibility: hidden;}
        </style>
    '''
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)
    

def init_login_view():
    view_sidebar.draw_signin_sidebar()
    st.title('Please enter developer password')

    pw = st.text_input("Password:", type="password")

    login_button = st.button('Sign in')
    if login_button:
        if pw == st.secrets.dev.pw:
            st.session_state.signed_in = True
    #facebook_button = st.button('Sign in with Facebook')
    #linkedin_button = st.button('Sign in with LinkedIn')

    #if google_button:
    #    authentication.sign_in('google')
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
