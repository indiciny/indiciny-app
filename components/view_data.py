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


def load_data(meta, data_index):
    data_name = meta['name']
    st.session_state.data_objects[data_index]['data_selection'] = data_name
    st.session_state.data_objects[data_index]['data_code'] = "data/" + meta['data_location']
    st.session_state.data_objects[data_index]['data_selection_expanded'] = False
    st.session_state.data_objects[data_index]['data_code_ran'] = True
    st.session_state.data_objects[data_index]['data_type'] = meta['type']



def draw_source(data_index):
    if data_index == 0:
        st.write("## Data selection")
    #else:
    #    st.write("**Data source "+str(data_index+1)+"**")
    meta = st.session_state.data_meta
    data_index = str(data_index)

    if data_index in st.session_state.data_objects:
        if st.session_state.data_objects[data_index]['data_selection'] != "-":
            idx = (list(meta.keys())).index(st.session_state.data_objects[data_index]['data_selection'])
            data_indexed = True
        else:
            idx = 0
            data_indexed = False
    else:

        idx = 0
        data_indexed = False
    data_source = st.selectbox('src', meta, index=idx, label_visibility="collapsed", key="datasrc"+str(data_index))
    if data_source != '-':
        if data_indexed:
            if st.session_state.data_objects[data_index]['data_selection'] != data_source:
                session_state.reset_after_data_selection(data_index, data_source)
        else:
            session_state.reset_after_data_selection(data_index, data_source)
            #st.session_state.data_objects[data_index]['data_selection_expanded'] = True
        #session_state.set_new_session_state('data_selection_expanded', True)
        source_expander = st.expander("Details / Load", expanded=st.session_state.data_objects[data_index]['data_selection_expanded'])
        if source_expander.expanded:
            with source_expander:
                st.write("Data source information")
                data_meta = meta[data_source]
                st.write("Source: " + data_meta['source'])
                st.write("License: " + data_meta['license'])
                st.write("Categories: " + ', '.join(data_meta['categories']))

                btn_load_data = st.button('Load data', key="btn"+str(data_index))
                if btn_load_data:
                    with st.spinner('Loading data...'):
                        load_data(data_meta, data_index)

    else:
        if data_indexed:
            if st.session_state.data_objects[data_index]['data_selection'] != '-':
                session_state.reset_after_data_selection(data_index, data_source)
        else:
            session_state.reset_after_data_selection(data_index, data_source)
        #session_state.reset_after_data_selection()



def draw_source_view(data_index):
    data_index = str(data_index)
    if data_index in st.session_state.data_objects:

        if st.session_state.data_objects[data_index]['data_code_ran']:
            st.session_state['data_type'] = st.session_state.data_objects[data_index]['data_type']

            #prerunparams = st.session_state.data_params.copy()
            check_data_change = False
            if data_index in st.session_state.returned_data:
                if st.session_state.returned_data[data_index] is not None:
                    prerundata = st.session_state.returned_data[data_index].copy()
                    check_data_change = True

            data_handler.run_private_code(st.session_state.data_objects[data_index]['data_code'], data_index)
            if check_data_change:
                if not prerundata.equals(st.session_state.returned_data[data_index]):
                    #st.session_state.preprocessing_params = {}
                    #st.session_state.method_selection = "-"
                    st.session_state.returned_data[data_index] = None
                    if data_index in st.session_state.data:
                        st.session_state.data.pop(data_index)

            if st.session_state.returned_data[data_index] is not None:
                #st.session_state.data_dict[data_index] = st.session_state.returned_data[data_index]
                st.session_state.data[data_index] = st.session_state.returned_data[data_index]

                #session_state.set_session_state('data', st.session_state.returned_data[data_index])
                st.session_state.original_data[data_index] = st.session_state.returned_data[data_index]

                #session_state.set_session_state('original_data', st.session_state.returned_data[data_index])
                #st.session_state
                #session_state.set_session_state('data_selection_expanded', False)
                #st.write(st.session_state.data_dict[data_index].head())

                    #st.session_state.data = st.session_state.data_dict['0']


