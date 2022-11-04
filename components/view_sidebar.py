import streamlit as st
from . import session_state
from pandas.api.types import is_numeric_dtype
import re


def draw_signin_sidebar():
    with st.sidebar:
        st.markdown("# Welcome to indiciny _beta_")
        st.markdown("### Data privacy")
        st.write("""
        We do not sell your data. We provide access to publicly available data.
        We only track your actions for improving our service for you. We also love feedback:
        """)
        st.write('_feedback_option_')
        with st.expander('Terms and conditions'):
            st.write('lorem ipsum')


def draw_sidebar():
    with st.sidebar:
        st.write("Welcome *" + session_state.get_session_state('user_email') + "*!")
        st.markdown("# Data analysis")
        st.write("It's easy: select a data source and an analysis method to perform on it.")
        #if session_state.get_session_state('data_loaded'):
            #st.write('---')
            #draw_data_filter()


def draw_counter():
    st.sidebar.write('---')
    with st.sidebar:
        col1, col2 = st.columns(2)
        col1.metric("Data loads", st.session_state.data_loads)
        col2.metric("Method executions", st.session_state.method_executions)


def update_data_filter(filters):
    filtered_data = st.session_state.original_data
    st.sidebar.write(filters)
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
        col1, col2 = st.columns(2)
        col1.write("Select data filters")
        if st.session_state.data_filtered:
            reset_filters = col2.button("Reset filters")
            if reset_filters:
                update_data_filter('')
                st.session_state.data_filtered = False
                st.experimental_rerun()

        filters = st.multiselect("Select data filters", st.session_state.original_data.columns,
                                   label_visibility="collapsed")

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
