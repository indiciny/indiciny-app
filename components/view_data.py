import streamlit as st
import json
from . import data_handler
from . import session_state
from . import view_preprocessing


ttl_value = 600


def load_data_meta():
    meta = data_handler.get_private_file("data_meta.json")
    meta = json.loads(meta)
    return meta


def load_data(meta):
    st.session_state.data_name = st.session_state.selected_data_meta['name']
    st.session_state.data_code = "data/" + meta['data_location']
    session_state.set_session_state('data_selection_expanded', False)
    st.session_state.data_code_ran = True
    st.session_state.data_selection = st.session_state.data_name


def draw_source():
    st.write("### Data selection")
    meta = st.session_state.data_meta
    idx = (list(meta.keys())).index(st.session_state.data_selection)
    data_source = st.selectbox('src', meta, index=idx, label_visibility="collapsed")
    if data_source != '-':
        if st.session_state.persistent_state["data_selection"] != data_source:
            session_state.reset_after_data_selection()
        session_state.set_new_session_state('data_selection_expanded', True)
        source_expander = st.expander("Details / Load", expanded=st.session_state.data_selection_expanded)
        if source_expander.expanded:
            with source_expander:
                st.write("Data source information")
                session_state.set_session_state('selected_data_meta', meta[data_source])
                st.write("Source: " + st.session_state.selected_data_meta['source'])
                st.write("License: " + st.session_state.selected_data_meta['license'])
                st.write("Categories: " + ', '.join(st.session_state.selected_data_meta['categories']))

                btn_load_data = st.button('Load data')
                if btn_load_data:
                    with st.spinner('Loading data...'):
                        load_data(st.session_state.selected_data_meta)

    else:
        session_state.reset_after_data_selection()


def draw_source_view():
    if st.session_state.data_code_ran:
        #prerunparams = st.session_state.data_params.copy()
        check_data_change = False
        if st.session_state.returned_data is not None:
            prerundata = st.session_state.returned_data.copy()
            check_data_change = True
        data_handler.run_private_code(st.session_state.data_code)
        if check_data_change:
            if not prerundata.equals(st.session_state.returned_data):
                st.session_state.preprocessing_params = {}
                st.session_state.method_selection = "-"

        if st.session_state.returned_data is not None:
            session_state.set_session_state('data', st.session_state.returned_data)
            session_state.set_session_state('original_data', st.session_state.returned_data)
            session_state.set_session_state('data_selection_expanded', False)
            view_preprocessing.draw_preprocessing()
            sv_container = st.container()
            with sv_container:
                st.dataframe(st.session_state.data)
