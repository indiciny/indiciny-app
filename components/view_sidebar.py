import streamlit as st
from . import session_state
from . import data_handler
import pandas as pd
from pandas.api.types import is_numeric_dtype
import re


def draw_sidebar():
    with st.sidebar:
        st.write("Welcome *" + st.session_state.userlogin + "*! [(sign out)](https://indiciny.com/wp-login.php?action=logout)")
        st.markdown("# Data analysis")
        st.write("It's easy: select a data source and an analysis method to perform on it.")
        draw_examples_part()


def draw_examples_part():
    st.write('---')
    #examples = data_handler.get_examples()
    #wanted = '.json'
    #examples = list(filter(lambda x: x.endswith(wanted), examples))
    #examples = pd.DataFrame(examples, columns=['file'])
    #examples['name'] = examples['file'].str.split(r"\.json", expand=True)[0]
    #top_row = pd.DataFrame({'name': '-'}, index=[0])
    #examples = pd.concat([top_row, examples.loc[:]]).reset_index(drop=True)
    examples = ['-', 'Line chart of GDP']
    example_selection = st.selectbox("Load example", examples) #.name)
    if example_selection != '-':
        st.warning('Loading this example will overwrite your current selections! Do you want to continue?')
        overwrite = st.button('Continue')
        if overwrite:
            #example_file = examples.loc[examples['name'] == example_selection]['file'].values[0]
            #st.write(example_file)
            state_file = "example_" + example_selection + ".json"
            session_state.load_persistent_state(state_file)
            session_state.save_persistent_state(True)
            #st.experimental_rerun()


def draw_data_ops():
    with st.sidebar:
        if st.session_state.data is not None:
            st.write('---')
            btn_save_data = st.button('Save data')
            if btn_save_data:
                st.text_input("Type data name")
            st.write('---')
            st.download_button("Download data", st.session_state.data.to_csv(index=False), file_name=st.session_state.data_selection + ".csv")
            st.write('---')


def draw_counter():
    st.sidebar.write('---')
    with st.sidebar:
        col1, col2 = st.columns(2)
        col1.metric("Data loads", st.session_state.data_loads)
        col2.metric("Method executions", st.session_state.method_executions)


def update_data_filter(filters):
    filtered_data = st.session_state.original_data
    for data_filter in filters:
        d_filter = filters[data_filter]
        dtype = d_filter['type']
        if dtype == 'string':
            filtered_data = filtered_data[filtered_data[data_filter].str.contains(d_filter['filter'], flags=re.IGNORECASE)]
        elif dtype == 'categories':
            filtered_data = filtered_data[filtered_data[data_filter].isin(d_filter['filter'])]
        elif dtype == 'range':
            filtered_data = filtered_data[filtered_data[data_filter] >= d_filter['filter'][0]]
            filtered_data = filtered_data[filtered_data[data_filter] <= d_filter['filter'][1]]
        else:
            st.warning('Not yet implemented', icon="⚠")
    st.session_state.data = filtered_data


def draw_data_filter():
    with st.sidebar:
        st.write('---')
        col1, col2 = st.columns(2)
        col1.write("Select data filters")
        if st.session_state.data_filtered:
            reset_filters = col2.button("Reset filters")
            if reset_filters:
                update_data_filter('')
                st.session_state.data_filtered = False
                st.session_state.data_filter_select = []
                st.experimental_rerun()

        filters = st.multiselect("Select data filters", st.session_state.original_data.columns,
                                 label_visibility="collapsed",
                                 key='data_filter_select')

        categorical = st.session_state.original_data.select_dtypes(include=['category', object]).columns
        dfdict = {}
        if len(filters) > 0:
            st.session_state['data_filters_form'] = st.form('thisform')
            with st.session_state['data_filters_form']:
                for dfilter in filters:
                    if filters.index(dfilter) > 0:
                        st.write('---')
                    st.write(dfilter)
                    if st.session_state.original_data[dfilter].name in categorical:
                        if st.session_state.original_data[dfilter].nunique(dropna=True) < 10:
                            catfilters = st.multiselect("Select categories", st.session_state.original_data[dfilter].unique())
                            dfdict[dfilter] = {'filter': catfilters, 'type': 'categories'}
                        else:
                            dstring = st.text_input("Enter text filter for: " + dfilter)
                            if dstring:
                                dfdict[dfilter] = {'filter': dstring, 'type': 'string'}
                    elif is_numeric_dtype(st.session_state.original_data[dfilter]):
                        dmin = round(float(st.session_state.original_data[dfilter].dropna().min()))
                        dmax = round(float(st.session_state.original_data[dfilter].dropna().max()))
                        if (dmax - dmin) > 100:
                            dstep = round((dmax - dmin) / 10)
                        else:
                            dstep = 1
                        values = st.slider(
                            "Filter by: " + dfilter,
                            min_value=dmin, max_value=dmax, value=(dmin, dmax),
                            step=dstep
                        )
                        # if values ne [dmin,dmax]:
                        dfdict[dfilter] = {'filter': values, 'type': 'range'}

                    else:
                        st.warning('Not yet implemented', icon="⚠")

                btn_update_filter = st.form_submit_button('Update filter')
            if btn_update_filter:
                st.session_state.data_filtered = True
                update_data_filter(dfdict)
                st.experimental_rerun()
        else:
            st.session_state.data = st.session_state.original_data
