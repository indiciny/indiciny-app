import streamlit as st
from . import view_sidebar
from . import view_data
from . import view_method
from . import data_handler
from . import session_state
import time


def check_user_session():
    user_id = session_state.get_session_state('query_params')['userlogin'][0]
    param_otac = session_state.get_session_state('query_params')['otac'][0]
    login_query = "SELECT `user_otac`,`valid_until` FROM `indiciny_otac` WHERE `user_id`='" + user_id + "';"
    query_result = data_handler.run_db_query(login_query)
    otac_time = query_result[0][1] > time.time()
    otac_check = (query_result[0][0] == param_otac)
    if otac_time and otac_check:
        session_state.set_session_state('user_id', user_id)
        init_app_view()
    else:
        st.write("Visit https://indiciny.com")


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
