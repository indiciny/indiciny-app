import streamlit as st
from . import view_data
from . import view_method
from . import data_handler
from ftplib import FTP
import json
import io
import copy
import os


def set_session_state(key, value):
    st.session_state[key] = value


def set_new_session_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value


def get_session_state(key):
    if key not in st.session_state:
        set_session_state(key, '')
    return st.session_state[key]


def increase_data_counter(increment):
    st.session_state.data_loads = st.session_state.data_loads + increment


def increase_method_counter(increment):
    st.session_state.method_executions = st.session_state.method_executions + increment


#def update_persistent_state(key, value):
    #st.session_state[key] = value
    #st.session_state.persistent_state[key] = value


def reset_states():
    st.session_state.returned_data = None
    st.session_state.data = None
    #st.session_state.data = None



def reset_persistent_state():
    st.session_state['persistent_state'] = {
        "data_selection": "-",
        "data_selection_expanded": True,
        "data_params": {},
        "data_code": "",
        "data_code_ran": False,
        "preprocessing_expanded": False,
        "preprocessing_params": {},
        "method_selection": "-",
        "method_selection_expanded": True,
        "method_params": {},
        "method_code": "",
        "method_code_ran": False,
        "user_changed_method_params": st.session_state['user_changed_method_params']
    }
    for key, value in st.session_state.persistent_state.items():
        st.session_state[key] = value


def reset_after_data_selection():
    reset_states()
    st.session_state.persistent_state = {
        "data_selection": st.session_state.data_selection,
        "data_selection_expanded": True,
        "data_params": {},
        "data_code": "",
        "data_code_ran": False,
        "preprocessing_expanded": False,
        "preprocessing_params": {},
        "method_selection": "-",
        "method_selection_expanded": True,
        "method_params": {},
        "method_code": "",
        "method_code_ran": False,
        "user_changed_method_params": False
    }
    for key, value in st.session_state.persistent_state.items():
        if key != "data_selection":
            st.session_state[key] = value
    #st.experimental_rerun()


def reset_after_method_selection():
    st.session_state.persistent_state = {
        "data_selection": st.session_state.data_selection,
        "data_selection_expanded": st.session_state.data_selection_expanded,
        "data_params": st.session_state.data_params,
        "data_code": st.session_state.data_code,
        "data_code_ran": st.session_state.data_code_ran,
        "preprocessing_expanded": st.session_state.preprocessing_expanded,
        "preprocessing_params": st.session_state.preprocessing_params,
        "method_selection": st.session_state.persistent_state['method_selection'],
        "method_selection_expanded": True,
        "method_params": st.session_state.persistent_state['method_params'],
        "method_code": "",
        "method_code_ran": False,
        "user_changed_method_params": False
    }
    #st.write(st.session_state.persistent_state)
    persist = ["data_selection","data_selection_expanded","data_params","data_code","data_code_ran","preprocessing_expanded","preprocessing_params","method_selection","method_params"]
    for key, value in st.session_state.persistent_state.items():
        if key not in persist:
            st.session_state[key] = value


def load_persistent_state(state_name, directory):
    reset_persistent_state()
    #state_name = "state_" + st.session_state.userlogin + ".json"
    with open(state_name, "wb") as file:
        with FTP(st.secrets.ftp.ftp_url, st.secrets.ftp.ftp_user, st.secrets.ftp.ftp_pw) as ftp:
            if directory != '':
                try:
                    ftp.cwd(directory)
                except:
                    ftp.mkd(directory)
                    ftp.cwd(directory)
            if state_name in ftp.nlst():
                ftp.retrbinary(f"RETR {state_name}", file.write)
                found_state = True
            else:
                found_state = False
    if found_state:
        try:
            file = open(state_name, "r")
            content = file.read()
            fread_success = True
        except:
            fread_success = False
            del st.session_state['only_once']
            st.experimental_rerun()
        if fread_success:
            st.session_state.persistent_state = dict(json.loads(content))
    try:
        os.remove(state_name)
    except:
        pass

    for key, value in st.session_state.persistent_state.items():
        st.session_state[key] = value
        #st.write(st.session_state[key])

    st.session_state['previous_state'] = json.dumps(st.session_state.persistent_state)
    #st.write(st.session_state['previous_state'])


def save_persistent_state(force, state_name, directory):
    #previous_state = st.session_state.persistent_state.copy()
    #previous_state = copy.deepcopy(st.session_state.persistent_state)
    #previous_state = json.loads(json.dumps(st.session_state.persistent_state))

    #st.write(st.session_state.method_selection)
    #st.write(st.session_state.preprocessing_params)
    st.session_state.persistent_state = {
        "data_selection": st.session_state.data_selection,
        "data_selection_expanded": st.session_state.data_selection_expanded,
        "data_params": st.session_state.data_params,
        "data_code": st.session_state.data_code,
        "data_code_ran": st.session_state.data_code_ran,
        "preprocessing_expanded": st.session_state.preprocessing_expanded,
        "preprocessing_params": st.session_state.preprocessing_params,
        "method_selection": st.session_state.method_selection,
        "method_selection_expanded": st.session_state.method_selection_expanded,
        "method_params": st.session_state.method_params,
        "method_code": st.session_state.method_code,
        "method_code_ran": st.session_state.method_code_ran,
        "user_changed_method_params": st.session_state.user_changed_method_params
    }

    #if st.session_state.persistent_state != previous_state or force:
    #previous_state = json.loads(json.dumps(st.session_state.previous_state))
    previous_state = st.session_state['previous_state']
    current_state = json.dumps(st.session_state.persistent_state)
    #st.write(previous_state)
    #st.write(current_state)

    if previous_state != current_state or force:
        with st.spinner("Saving state..."):
            state = json.dumps(st.session_state.persistent_state)
            bio = io.BytesIO()
            bio.write(state.encode())
            bio.seek(0)
            #state_name = "state_" + st.session_state.uid + ".json"
            with FTP(st.secrets.ftp.ftp_url, st.secrets.ftp.ftp_user, st.secrets.ftp.ftp_pw) as ftp:
                if directory != '':
                    try:
                        ftp.cwd(directory)
                    except:
                        ftp.mkd(directory)
                        ftp.cwd(directory)
                ftp.storbinary(f'STOR {state_name}', bio)

            st.session_state['previous_state'] = json.dumps(st.session_state.persistent_state)
            data_handler.log_transaction('state_change')

        #st.experimental_rerun()
        #st.sidebar.write('uploaded')
    #else:
        #st.sidebar.write('unchanged')
