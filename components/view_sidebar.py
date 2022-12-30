import streamlit as st
from . import session_state
from . import data_handler
import pandas as pd
from pandas.api.types import is_numeric_dtype
import re
import time


def draw_sidebar():
    with st.sidebar:
        st.write(
            "Welcome *" + st.session_state.userlogin + "*! [(sign out)](https://indiciny.com/wp-login.php?action=logout)")
        st.markdown("# Data analysis")
        st.write("It's easy: select a data source and an analysis method to perform on it.")
        exp = st.expander("Options")
        if exp.expanded:
            with st.expander("Options"):
                draw_load_state('examples', 'example_', "Load example")
                st.write('---')
                state_list = draw_load_state(st.session_state.uid + "/saved", "saved_state_", "Load saved state")
                col1, col2 = st.columns(2)
                btn_save_state = col2.button('Save current state')
                txt = col1.text_input("dn", label_visibility="collapsed", placeholder="Enter state name")
                if btn_save_state:
                    if txt == '':
                        name = time.strftime('%Y-%m-%dT%H:%M:%SZ')
                    else:
                        name = txt
                    state_file = "saved_state_" + name + ".json"
                    session_state.save_persistent_state(True, state_file, st.session_state.uid + "/saved")

                if not state_list.empty:
                    delete_states(state_list)


def draw_examples_part():
    st.write('---')
    examples = data_handler.get_states('examples')
    examples = list(filter(lambda x: x.endswith('.json'), examples))
    examples = pd.DataFrame(examples, columns=['file'])
    examples['name'] = examples['file'].str.split(r"\.json", expand=True)[0]
    examples['name'] = examples['name'].str.replace('example_', '')
    top_row = pd.DataFrame({'name': '-'}, index=[0])
    examples = pd.concat([top_row, examples.loc[:]]).reset_index(drop=True)
    example_selection = st.selectbox("Load example", examples)
    if example_selection != '-':
        st.warning('Loading this example will overwrite your current selections! Do you want to continue?')
        overwrite = st.button('Continue')
        if overwrite:
            example_file = "example_" + example_selection + ".json"
            session_state.load_persistent_state(example_file, 'examples')
            state_file = "state_" + st.session_state.uid + ".json"
            session_state.save_persistent_state(True, state_file, st.session_state.uid)


def draw_load_state(directory, prefix, heading):
    try:
        states = data_handler.get_states(directory)
        states = list(filter(lambda x: x.endswith('.json'), states))
        states = pd.DataFrame(states, columns=['file'])
        states['name'] = states['file'].str.split(r"\.json", expand=True)[0]
        states['name'] = states['name'].str.replace(prefix, '')
        top_row = pd.DataFrame({'name': '-'}, index=[0])
        states = pd.concat([top_row, states.loc[:]]).reset_index(drop=True)
        state_selection = st.selectbox(heading, states)
        if state_selection != '-':
            st.warning('Loading this state will overwrite your current selections! Do you want to continue?')
            overwrite = st.button('Continue')
            if overwrite:
                state_file = prefix + state_selection + ".json"
                session_state.load_persistent_state(state_file, directory)
                state_file = "state_" + st.session_state.uid + ".json"
                session_state.save_persistent_state(True, state_file, st.session_state.uid)
        return states
    except Exception as e:
        st.write(e)
        return pd.DataFrame()


def delete_states(state_list):
    state_selection = st.multiselect('Select states for deletion', state_list.name)
    if state_selection:
        st.warning('Are you sure?')
        delete = st.button('Delete')
        if delete:
            for state in state_selection:
                state_file = "saved_state_" + state + ".json"
                data_handler.delete_files(st.session_state.uid + "/saved", state_file)
            st.experimental_rerun()


def draw_data_ops():
    with st.sidebar:
        if st.session_state.data is not None:
            st.write('---')
            #st.download_button("Download data", st.session_state.data.to_csv(index=False), file_name=st.session_state.data_selection + ".csv")
            st.write('---')


def draw_counter():
    st.sidebar.write('---')
    with st.sidebar:
        col1, col2 = st.columns(2)
        col1.metric("Data loads", st.session_state.data_loads)
        col2.metric("Method executions", st.session_state.method_executions)
