import streamlit as st
import json
from . import data_handler
from . import session_state


ttl_value = 600


def load_data_meta():
    meta = data_handler.get_private_file("data_meta.json")
    meta = json.loads(meta)
    return meta


@st.cache(ttl=ttl_value)
def load_data(meta):
    if meta['data_type'] == 'csv':
        data = data_handler.get_public_csv(meta['data_location'])
        return data


def draw_source():
    st.write("### Data selection")
    meta = st.session_state.data_meta
    data_source = st.selectbox('Data source selection', meta, label_visibility="collapsed")
    if data_source != '-':
        session_state.set_new_session_state('source_expanded', True)
        source_expander = st.expander("Details / Load", expanded=st.session_state.source_expanded)
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
                        data = load_data(st.session_state.selected_data_meta)
                        session_state.set_session_state('data_loaded', True)
                        session_state.set_session_state('data', data)
                        session_state.set_session_state('original_data', data)
                        session_state.increase_data_counter(1)
                        data_handler.log_transaction('data', st.session_state.selected_data_meta['name'])
    else:
        session_state.set_session_state('data_loaded', False)


def draw_source_view():
    if st.session_state.data_loaded:
        session_state.set_session_state('source_expanded', False)
        sv_container = st.container()
        with sv_container:
            st.dataframe(st.session_state.data)
