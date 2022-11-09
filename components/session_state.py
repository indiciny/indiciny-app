import streamlit as st
from . import view_data
from . import view_method
from . import data_handler


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
