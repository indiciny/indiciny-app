import streamlit as st
import components.session_state as session_state
import components.view_data as view_data
import components.view_preprocessing as view_preprocessing
import components.view_method as view_method
import components.view_sidebar as view_sidebar
import components.data_handler as data_handler
import mysql.connector
import time
import pandas as pd


def initiate_states():
    st.session_state['data'] = None
    st.session_state['data_meta'] = view_data.load_data_meta()
    st.session_state['data_loaded'] = False
    st.session_state['data_loads'] = 0
    st.session_state['data_code_ran'] = False
    st.session_state['data_filtered'] = False
    st.session_state['execute_code'] = False
    st.session_state['method_meta'] = view_method.load_method_meta()
    st.session_state['method_executed'] = False
    st.session_state['method_executions'] = 0
    st.session_state['method_code_ran'] = False
    st.session_state['returned_data'] = None
    st.session_state['user_changed_method_params'] = False


def hide_header():
    hide_decoration_bar_style = '''
                <style>
                    header {visibility: hidden;}
                </style>
            '''
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


def user_id_affinity(user_email):
    # Connect to the database
    cnx = mysql.connector.connect(**st.secrets["tradb"])

    # Create a cursor
    cursor = cnx.cursor()

    # Construct the INSERT IGNORE INTO statement
    sql = """
    INSERT IGNORE INTO indiciny_user_affinity (user_mail)
    VALUES (%s)
    """

    # Execute the statement
    cursor.execute(sql, (user_email,))

    # Read the record that was just inserted or updated
    sql = "SELECT user_id FROM indiciny_user_affinity WHERE user_mail = %s"
    cursor.execute(sql, (user_email,))

    # Fetch the record
    record = (cursor.fetchone())[0]

    # Commit the transaction
    cnx.commit()

    # Close the cursor and connection
    cursor.close()
    cnx.close()
    return record



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
                st.session_state.userlogin = st.session_state.query_params['userlogin'][0]
                login = st.session_state.userlogin
                st.session_state.otac = st.session_state.query_params['otac'][0]
                conn = mysql.connector.connect(**st.secrets["wpmysql"]) #data_handler.connect_wp_db()
                login_query = "SELECT `user_otac`,`valid_until` FROM `indiciny_otac` WHERE `user_id`='" + login + "';"
                with conn.cursor() as cursor:
                    cursor.execute(login_query)
                    query_result = cursor.fetchall()

                otac_time = query_result[0][1] > time.time()
                otac_check = (query_result[0][0] == st.session_state.otac)
                if otac_time and otac_check:
                    initiate_states()
                    st.session_state.uid = str(user_id_affinity(st.session_state.userlogin))
                    state_file = "state_" + st.session_state.uid + ".json"
                    #st.write(state_file + " " + st.session_state.uid)
                    session_state.load_persistent_state(state_file, st.session_state.uid)
                    st.session_state.authorized = True
                    data_handler.log_transaction('login')



    if st.session_state.authorized:

        view_sidebar.draw_sidebar()

        view_data.draw_source()
        view_data.draw_source_view()
        #if st.session_state.data
        if st.session_state.data is not None:
            btn_merge_data = st.button('Merge data')
            if btn_merge_data:
                st.write('---')
                st.write('secondary data...')


        st.write('___')
        view_method.draw_method()
        view_method.draw_method_view()

        #view_sidebar.draw_counter()
        view_sidebar.draw_data_ops()

        view_session_state()

        #btn_savestate = st.button('Save State')
        #if btn_savestate:
        #st.write(st.session_state.persistent_state)
        state_file = "state_" + st.session_state.uid + ".json"
        session_state.save_persistent_state(False, state_file, st.session_state.uid)

    else:
        st.write("Visit https://indiciny.com/app")


def view_session_state():
    if st.session_state.userlogin == st.secrets.developer:
        with st.sidebar:
            with st.expander("Details / Load"):
                st.session_state.persistent_state
                st.session_state


if __name__ == "__main__":
    init_app()
