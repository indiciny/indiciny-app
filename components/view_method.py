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
    #data_handler.run_private_code(st.session_state.method_code, {"data": st.session_state.data})
    session_state.set_session_state('method_selection_expanded', False)
    st.session_state.method_code_ran = True


def filter_methods(category):
    return st.session_state.method_meta


def draw_method():
    st.write("### Analysis method")
    meta = st.session_state.method_meta
    data_method = st.selectbox('Analysis method', meta, label_visibility="collapsed", key="method_selection")
    if data_method != '-':
        session_state.set_new_session_state('method_expanded', True)
        method_expander = st.expander("Details / Load", expanded=st.session_state.method_selection_expanded)
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
                            load_method(st.session_state.selected_method_meta)
                            #session_state.set_session_state('method_executed', True)
                            #session_state.set_session_state('method', method)
                            #session_state.increase_method_counter(1)
                            #data_handler.log_transaction('method', st.session_state.selected_method_meta['name'])


def draw_method_view():
    #if 'returned_method' not in st.session_state and st.session_state.method_code_ran:
    if st.session_state.method_code_ran:
        #data = {"data": st.session_state.data}
        #params = {**data, **st.session_state.method_params}
        data_handler.run_private_code(st.session_state.method_code)

    #if 'returned_method' in st.session_state:
        #if st.session_state.returned_method is not None: #and st.session_state.set_data:
            #st.session_state.set_data = False
            #session_state.set_session_state('data_loaded', True)
            #session_state.set_session_state('data', st.session_state.returned_data)
            #session_state.set_session_state('original_data', st.session_state.returned_data)
            #session_state.increase_data_counter(1)
            #data_handler.log_transaction('data', st.session_state.selected_data_meta['name'])
            #session_state.set_session_state('method_selection_expanded', False)
            #mv_container = st.container()
            #with mv_container:
                #exec(st.session_state.method, {"data": st.session_state.data})

    #if st.session_state.data_loaded:
        #session_state.set_session_state('data_selection_expanded', False)
        #sv_container = st.container()
        #with sv_container:
            #st.dataframe(st.session_state.data)
            #st.download_button('Download data', st.session_state.data.to_csv(index=False), file_name=st.session_state.data_selection + ".csv")
#def draw_method_view():
    #if st.session_state.data_loaded and st.session_state.method_executed:
        #session_state.set_session_state('method_expanded', False)
        #mv_container = st.container()
        #with mv_container:
            #exec(st.session_state.method, {"data": st.session_state.data})
