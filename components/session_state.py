import streamlit as st


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

    # Initialize session state variables
    if 'signed_in' not in st.session_state:
        st.session_state['signed_in'] = False
        st.session_state['data_loaded'] = False
        st.session_state['data_loads'] = 0
        st.session_state['data_source'] = ''
        st.session_state['method_executed'] = False
        st.session_state['method_executions'] = 0
        st.session_state['dont_refresh'] = False
        st.session_state['data_filtered'] = False


def set_session_state(key, value):
    st.session_state[key] = value


def get_session_state(key):
    return st.session_state[key]
