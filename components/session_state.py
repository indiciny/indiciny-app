import streamlit as st
from . import view_data
from . import view_method


def init_app():
    # Set page configuration
    st.set_page_config(
        page_title="indiciny",
        page_icon="ℹ️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            # 'Get Help': 'https://www.extremelycoolapp.com/help',
            # 'Report a bug': "https://www.extremelycoolapp.com/bug",
            # 'About': "/pages/01_🗒️ About.py"
        }
    )

    hide_decoration_bar_style = '''
            <style>
                header {visibility: hidden;}
            </style>
        '''
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

    # Initialize session state variables
    if 'signed_in' not in st.session_state:
        st.session_state['query_params'] = get_query_params()
        st.session_state['access_token'] = ''
        st.session_state['signed_in'] = False #authentication.check_sign_in(st.session_state['query_params'])
        st.session_state['data_meta'] = view_data.load_data_meta()
        st.session_state['method_meta'] = view_method.load_method_meta()
        st.session_state['data_loaded'] = False
        st.session_state['data_loads'] = 0
        st.session_state['method_executed'] = False
        st.session_state['method_executions'] = 0
        st.session_state['dont_refresh'] = False
        st.session_state['data_filtered'] = False
        st.write(st.session_state['query_params'])
    

def set_session_state(key, value):
    st.session_state[key] = value


def set_new_session_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value


def get_session_state(key):
    if key not in st.session_state:
        set_session_state(key, '')
    return st.session_state[key]


def get_query_params():
    returns = st.experimental_get_query_params()
    return returns


def increase_data_counter(increment):
    st.session_state.data_loads = st.session_state.data_loads + increment


def increase_method_counter(increment):
    st.session_state.method_executions = st.session_state.method_executions + increment
