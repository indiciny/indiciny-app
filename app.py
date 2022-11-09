import components.session_state as session_state
import components.view_controller as view_controller
import streamlit as st
import mysql.connector
import time


def run():
    init_app()


def set_counters():
    st.session_state['data_loaded'] = False
    st.session_state['data_loads'] = 0
    st.session_state['method_executed'] = False
    st.session_state['method_executions'] = 0


def hide_header():
    hide_decoration_bar_style = '''
                <style>
                    header {visibility: hidden;}
                </style>
            '''
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


@st.experimental_singleton
def connect_wp_db():
    return mysql.connector.connect(**st.secrets["wpmysql"])


def init_app():
    # Set page configuration
    st.set_page_config(
        page_title="indiciny",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://indiciny.com',
            'Report a bug': 'https://indiciny.com',
            'About': 'https://indiciny.com'
        }
    )
    hide_header()
    if 'authorized' not in st.session_state:
        st.session_state.authorized = False
        st.session_state.query_params = st.experimental_get_query_params()
        if 'embedded' in st.session_state.query_params:
            if 'userlogin' and 'otac' in st.session_state.query_params:
            #if st.session_state.query_params['userlogin'] and st.session_state.query_params['otac']:
                st.session_state.userlogin = st.session_state.query_params['userlogin'][0]
                login = st.session_state.userlogin
                st.session_state.otac = st.session_state.query_params['otac'][0]
                conn = mysql.connector.connect(**st.secrets["wpmysql"]) #data_handler.connect_wp_db()
                login_query = "SELECT `user_otac`,`valid_until` FROM `indiciny_otac` WHERE `user_id`='" + login + "';"
                with conn.cursor() as cursor:
                    cursor.execute(login_query)
                    query_result = cursor.fetchall()

                otac_time = query_result[0][1] > time.time()
                otac_check = (query_result[0][0] == param_otac)
                if otac_time and otac_check:
                    st.session_state.authorized = True

    if st.session_state.authorized:
        set_counters()
        view_controller.init_app_view()
    else:
        st.write("Visit https://indiciny.com")


if __name__ == "__main__":
    run()
