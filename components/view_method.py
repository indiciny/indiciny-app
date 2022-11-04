import streamlit as st
import json
from . import data_handler
from . import session_state


ttl_value = 600


def load_method_meta():
    meta = data_handler.get_private_file("method_meta.json")
    meta = json.loads(meta)
    return meta


def load_method(meta):
    if meta['data_type'] == 'code':
        method = data_handler.run_private_code(meta['data_location'])
        return method


def filter_methods(category):
    return st.session_state.method_meta


def draw_method():
    st.write("### Analysis method")
    meta = st.session_state.method_meta
    data_method = st.selectbox('Analysis method', meta, label_visibility="collapsed")
    if data_method != '-':
        session_state.set_new_session_state('method_expanded', True)
        method_expander = st.expander("Details / Load", expanded=st.session_state.method_expanded)
        if method_expander.expanded:
            with method_expander:
                st.write("Analysis method information")
                session_state.set_session_state('selected_method_meta', meta[data_method])
                st.write("Source: " + st.session_state.selected_method_meta['source'])
                st.write("License: " + st.session_state.selected_method_meta['license'])
                st.write("Categories: " + ', '.join(st.session_state.selected_method_meta['categories']))

                if st.session_state.data_loaded:
                    btn_load_method = st.button('Analyze')
                    if btn_load_method:
                        with st.spinner('Analyzing...'):
                            method = load_method(st.session_state.selected_method_meta)
                            session_state.set_session_state('method_executed', True)
                            session_state.set_session_state('method', method)
                            session_state.increase_method_counter(1)


def draw_method_view():
    if st.session_state.data_loaded and st.session_state.method_executed:
        session_state.set_session_state('method_expanded', False)
        mv_container = st.container()
        with mv_container:
            exec(st.session_state.method, {"data": st.session_state.data})
