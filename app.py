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
import sys


def initiate_states():
    st.session_state['data'] = {}
    st.session_state['original_data'] = {}
    st.session_state['data_meta'] = view_data.load_data_meta()
    st.session_state['data_loaded'] = False
    st.session_state['data_loads'] = 0
    #st.session_state['data_code_ran'] = False
    st.session_state['data_filtered'] = False
    st.session_state['execute_code'] = False
    st.session_state['method_meta'] = view_method.load_method_meta()
    st.session_state['method_executed'] = False
    st.session_state['method_executions'] = 0
    st.session_state['method_code_ran'] = False
    st.session_state['returned_data'] = {}
    st.session_state['secondary_returned_data'] = {}
    st.session_state['user_changed_method_params'] = False
    st.session_state['secondary_added'] = False
    st.session_state['secondary_merged'] = False


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
        view_session_state()

        view_sidebar.draw_sidebar()

        view_data.draw_source(0)
        view_data.draw_source_view(0)
        #view_preprocessing.draw_preprocessing('0')

        if '0' in st.session_state.data:
            st.session_state.data['final'] = st.session_state.data['0']
            view_preprocessing.draw_preprocessing()


            sv_container = st.container()
            with sv_container:
                st.write('---')
                st.write("## Data preview")
                st.dataframe(st.session_state.data['final'])
            #view_preprocessing.draw_preprocessing()


        st.write('___')

        if len(st.session_state.analysis_objects) == 0:
            view_method.draw_method(0)
            view_method.draw_method_view(0)
        else:
            for n in range(0, len(st.session_state.analysis_objects)):
                view_method.draw_method(n)
                view_method.draw_method_view(n)

            ran = st.session_state.analysis_objects[str(len(st.session_state.analysis_objects)-1)]['analysis_code_ran']
            if ran:
                view_method.draw_method(len(st.session_state.analysis_objects))
                view_method.draw_method_view(len(st.session_state.analysis_objects))

        view_data_info()

        #view_sidebar.draw_counter()
        #view_sidebar.draw_data_ops()

        #view_session_state()

        #btn_savestate = st.button('Save State')
        #if btn_savestate:
        #st.write(st.session_state.persistent_state)
        state_file = "state_" + st.session_state.uid + ".json"
        session_state.save_persistent_state(False, state_file, st.session_state.uid)

    else:
        st.write("Visit https://indiciny.com/app")


def view_data_info():

    def print_dinf(id, classifier):
        if classifier:
            st.write(classifier + ": " + st.session_state.data_objects[id]['data_selection'])
            st.write(st.session_state.data_objects[id]['data_params'])
        shape = st.session_state.data[id].shape
        st.write("Rows: " + str(shape[0]) + " / Columns: " + str(shape[1]))
        size = round(sys.getsizeof(st.session_state.data[id]) / 1048576, 2)
        st.write("Size in MB: " + str(size))

    with st.sidebar:
        with st.expander("Data information"):
            if '0' in st.session_state.data:
                print_dinf('0', "Primary data source")
                st.write('---')
            if '1' in st.session_state.data:
                print_dinf('1', "Secondary data source")
                st.write('---')
            if 'final' in st.session_state.data:
                st.write('Merged data:')
                print_dinf('final', None)
                st.download_button("Download data", st.session_state.data['final'].to_csv(index=False),
                                   file_name="indiciny_data.csv")





def view_session_state():
    if st.session_state.userlogin == st.secrets.developer:
        with st.sidebar:
            with st.expander("Details / Load"):
                st.session_state.persistent_state
                st.session_state


if __name__ == "__main__":
    init_app()
