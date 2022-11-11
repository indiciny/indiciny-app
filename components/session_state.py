import streamlit as st
from . import view_data
from . import view_method
from . import data_handler
from ftplib import FTP
import json
import io


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


def update_persistent_state(key, value):
    st.session_state[key] = value
    st.session_state.persistent_state[key] = value


def reset_persistent_state():
    st.session_state.persistent_state = {
        "data_selection": "-",  #st.session_state.data_meta[0],
        "data_params": "",
        "data_original": "",
        "data_current": "",
        "method_selection": "-",
        "method_params": "",
        "method_code": ""
    }
    for key, value in st.session_state.persistent_state.items():
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


def save_persistent_state():
    st.session_state.persistent_state = {
        "data_selection": st.session_state.data_selection,
        "data_params": st.session_state.data_params,
        "data_original": st.session_state.data_original,
        "data_current": st.session_state.data_current,
        "method_selection": st.session_state.method_selection,
        "method_params": st.session_state.method_params,
        "method_code": st.session_state.method_code
    }
    state = json.dumps(st.session_state.persistent_state)
    bio = io.BytesIO()
    bio.write(state.encode())
    bio.seek(0)
    state_name = "state_" + st.session_state.userlogin + ".json"
    with FTP(st.secrets.ftp.ftp_url, st.secrets.ftp.ftp_user, st.secrets.ftp.ftp_pw) as ftp:
        ftp.storbinary(f'STOR {state_name}', bio)
