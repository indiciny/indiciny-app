import streamlit as st
from . import view_data
from . import view_method
from . import data_handler
from ftplib import FTP
import json
import io
import copy


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
    st.session_state.data = None



def reset_persistent_state():
    st.session_state.persistent_state = {
        "data_selection": "-",
        "data_selection_expanded": True,
        "data_params": {},
        "data_code": "",
        "data_code_ran": False,
        "method_selection": "-",
        "method_selection_expanded": True,
        "method_params": {},
        "method_code": "",
        "method_code_ran": False,
    }
    for key, value in st.session_state.persistent_state.items():
        st.session_state[key] = value


def reset_after_data_selection():
    st.session_state.persistent_state = {
        "data_selection": st.session_state.data_selection,
        "data_selection_expanded": True,
        "data_params": {},
        "data_code": "",
        "data_code_ran": False,
        "method_selection": "-",
        "method_selection_expanded": True,
        "method_params": {},
        "method_code": "",
        "method_code_ran": False,
    }
    for key, value in st.session_state.persistent_state.items():
        if key != "data_selection":
            st.session_state[key] = value


def reset_after_method_selection():
    st.session_state.persistent_state = {
        "data_selection": st.session_state.data_selection,
        "data_selection_expanded": st.session_state.data_selection_expanded,
        "data_params": st.session_state.data_params,
        "data_code": st.session_state.data_code,
        "data_code_ran": st.session_state.data_code_ran,
        "method_selection": st.session_state.persistent_state['method_selection'],
        "method_selection_expanded": True,
        "method_params": st.session_state.persistent_state['method_params'],
        "method_code": "",
        "method_code_ran": False,
    }
    #st.write(st.session_state.persistent_state)
    persist = ["data_selection","data_selection_expanded","data_params","data_code","data_code_ran","method_selection","method_params"]
    for key, value in st.session_state.persistent_state.items():
        if key not in persist:
            st.session_state[key] = value


def load_persistent_state():
    reset_persistent_state()
    state_name = "state_" + st.session_state.userlogin + ".json"
    with open(state_name, "wb") as file:
        with FTP(st.secrets.ftp.ftp_url, st.secrets.ftp.ftp_user, st.secrets.ftp.ftp_pw) as ftp:
            if state_name in ftp.nlst():
                ftp.retrbinary(f"RETR {state_name}", file.write)
                found_state = True
            else:
                found_state = False
    if found_state:
        file = open(state_name, "r")
        content = file.read()
        st.session_state.persistent_state = dict(json.loads(content))
    for key, value in st.session_state.persistent_state.items():
        st.session_state[key] = value


def save_persistent_state(force):
    #previous_state = st.session_state.persistent_state.copy()
    #previous_state = copy.deepcopy(st.session_state.persistent_state)
    previous_state = json.loads(json.dumps(st.session_state.persistent_state))
    #st.write(st.session_state.method_params)
    st.session_state.persistent_state = {
        "data_selection": st.session_state.data_selection,
        "data_selection_expanded": st.session_state.data_selection_expanded,
        "data_params": st.session_state.data_params,
        "data_code": st.session_state.data_code,
        "data_code_ran": st.session_state.data_code_ran,
        "method_selection": st.session_state.method_selection,
        "method_selection_expanded": st.session_state.method_selection_expanded,
        "method_params": st.session_state.method_params,
        "method_code": st.session_state.method_code,
        "method_code_ran": st.session_state.method_code_ran
    }

    if st.session_state.persistent_state != previous_state or force:
        state = json.dumps(st.session_state.persistent_state)
        bio = io.BytesIO()
        bio.write(state.encode())
        bio.seek(0)
        state_name = "state_" + st.session_state.userlogin + ".json"
        with FTP(st.secrets.ftp.ftp_url, st.secrets.ftp.ftp_user, st.secrets.ftp.ftp_pw) as ftp:
            ftp.storbinary(f'STOR {state_name}', bio)
        st.sidebar.write('uploaded')
    else:
        st.sidebar.write('unchanged')
