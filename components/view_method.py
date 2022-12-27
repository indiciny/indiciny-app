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
    st.session_state.method_name = st.session_state.selected_method_meta['name']
    st.session_state.method_code = "methods/" + meta['data_location']
    session_state.set_session_state('method_selection_expanded', False)
    st.session_state.method_code_ran = True


def filter_methods(category):
    return st.session_state.method_meta


def draw_method():
    st.write("### Analysis method")
    meta = st.session_state.method_meta
    idx = (list(meta.keys())).index(st.session_state.method_selection)
    data_method = st.selectbox('Analysis method', meta, index=idx, label_visibility="collapsed")
    if data_method != '-':
        if st.session_state.persistent_state["method_selection"] != data_method:
            session_state.reset_after_method_selection()

        session_state.set_new_session_state('method_expanded', True)
        method_expander = st.expander("Details / Load", expanded=st.session_state.method_selection_expanded)
        if method_expander.expanded:
            with method_expander:
                st.write("Analysis method information")
                session_state.set_session_state('selected_method_meta', meta[data_method])
                st.write("Source: " + st.session_state.selected_method_meta['source'])
                st.write("License: " + st.session_state.selected_method_meta['license'])
                st.write("Categories: " + ', '.join(st.session_state.selected_method_meta['categories']))

                if st.session_state.data is not None:
                    btn_load_method = st.button('Analyze')
                    if btn_load_method:
                        with st.spinner('Analyzing...'):
                            st.session_state['method_selection'] = data_method
                            load_method(st.session_state.selected_method_meta)
    else:
        session_state.reset_after_method_selection()
        #st.session_state.method_code_ran = False
        #st.session_state.method_code = ""
        #st.session_state.method_params = {}
        #st.session_state.user_changed_method_params = False


def draw_method_view():
    if st.session_state.method_code_ran:
        prerunparams = st.session_state.method_params.copy()
        data_handler.run_private_code(st.session_state.method_code, None)
        if prerunparams != st.session_state.method_params:
            st.session_state['user_changed_method_params'] = True
