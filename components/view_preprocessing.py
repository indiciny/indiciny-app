import streamlit as st
from . import session_state
from . import view_data
import wbdata
import pandas as pd
from pandas.api.types import is_numeric_dtype
import re
import sys


def update_data_filter(filters):
    filtered_data = st.session_state.data['final']
    for data_filter in filters:
        d_filter = filters[data_filter]
        dtype = d_filter['type']
        if dtype == 'string':
            filtered_data = filtered_data[filtered_data[data_filter].str.contains(d_filter['filter'], flags=re.IGNORECASE, na=False)]
        elif dtype == 'categories':
            if d_filter['filter']:
                filtered_data = filtered_data[filtered_data[data_filter].isin(d_filter['filter'])]
        elif dtype == 'range':
            if d_filter['filter']:
                filtered_data = filtered_data[filtered_data[data_filter] >= d_filter['filter'][0]]
                filtered_data = filtered_data[filtered_data[data_filter] <= d_filter['filter'][1]]
        else:
            st.warning('Not yet implemented', icon="⚠")
    st.session_state.data['final'] = filtered_data


def set_preprocessing_param(data_index, group, name, value):
    st.session_state.preprocessing_params[data_index][group][name] = value


def column_selection():
    st.write('Select columns:')
    group = 'column_selection'
    if group not in st.session_state.preprocessing_params:
        st.session_state.preprocessing_params[group] = st.session_state.data['final'].columns
        columns = st.session_state.data['final'].columns

    else:
        columns = st.session_state.preprocessing_params[group]
        columns[:] = [x for x in columns if (x in st.session_state.data['final'].columns)]

    with st.form('column_selection_form'):
        selected_columns = st.multiselect("Select columns", st.session_state.data['final'].columns,
                                          label_visibility="collapsed",
                                          default=list(columns))
        btn_update_columns = st.form_submit_button('Update columns')
    if btn_update_columns:
        st.session_state.preprocessing_params[group] = selected_columns
    st.session_state.data['final'] = st.session_state.data['final'][st.session_state.preprocessing_params[group]]

    return group, st.session_state.preprocessing_params[group]
    #st.session_state.preprocessing_params[group] = selected_columns
    #st.session_state.data['final'] = st.session_state.data['final'][selected_columns]
    #return group, selected_columns


def column_filters():
    st.write("Filter based on columns:")
    group = 'column_filter'
    if group not in st.session_state.preprocessing_params:
        st.session_state.preprocessing_params[group] = {}
        cf_values = []
    else:
        cf_values = list(st.session_state.preprocessing_params[group].keys())
        cf_values[:] = [x for x in cf_values if (x in st.session_state.data['final'].columns)]

    filters = st.multiselect("Select data filters", st.session_state.data['final'].columns,
                             label_visibility="collapsed",
                             default=cf_values)
    categorical = st.session_state.data['final'].select_dtypes(include=['category', object]).columns

    column_filter = st.session_state.preprocessing_params[group]

    dfdictnew = {}
    if len(filters) > 0:
        with st.form('column_filter_form'):
            for dfilter in filters:
                if filters.index(dfilter) > 0:
                    st.write('---')
                if st.session_state.data['final'][dfilter].name in categorical:
                    if st.session_state.data['final'][dfilter].nunique(dropna=True) < 10:
                        if dfilter in column_filter:
                            cfil = column_filter[dfilter]['filter']
                        else:
                            cfil = st.session_state.data['final'][dfilter].unique()
                        catfilters = st.multiselect("Select categories",
                                                    st.session_state.data['final'][dfilter].unique(),
                                                    default=cfil)
                        dfdictnew[dfilter] = {'filter': catfilters, 'type': 'categories'}
                    else:
                        dstring = st.text_input("Enter text filter for: " + dfilter)
                        if dstring:
                            dfdictnew[dfilter] = {'filter': dstring, 'type': 'string'}
                elif is_numeric_dtype(st.session_state.data['final'][dfilter]):
                    dmin = round(float(st.session_state.data['final'][dfilter].dropna().min()))
                    dmax = round(float(st.session_state.data['final'][dfilter].dropna().max()))
                    if (dmax - dmin) > 100:
                        dstep = round((dmax - dmin) / 10)
                    else:
                        dstep = 1
                    if dfilter in column_filter:
                        dmins = column_filter[dfilter]['filter'][0]
                        dmaxs = column_filter[dfilter]['filter'][1]
                        columns_filtered = True
                    else:
                        dmins = dmin
                        dmaxs = dmax

                    values = st.slider(
                        "Filter by: " + dfilter,
                        min_value=dmin, max_value=dmax, value=(dmins, dmaxs),
                        step=dstep
                    )
                    # if values ne [dmin,dmax]:
                    dfdictnew[dfilter] = {'filter': values, 'type': 'range'}

                else:
                    st.warning('Not yet implemented', icon="⚠")

            btn_update_filter = st.form_submit_button('Update filter')
        if btn_update_filter:
            columns_filtered = False
            st.session_state.preprocessing_params[group] = dfdictnew
        with st.spinner("Updating filters..."):
            update_data_filter(st.session_state.preprocessing_params[group])
        return group


def drop_na():
    label = "Drop empty values?"
    is_checked = False
    drop_nax = st.checkbox(label, value=is_checked)
    if drop_nax:
        st.session_state.data = st.session_state.data.dropna()


def add_secondary_data():
    part = 'add_secondary'
    if part not in st.session_state.preprocessing_params:
        st.session_state.preprocessing_params[part] = False

    cbx_sec_data = st.checkbox('Add secondary data', value=st.session_state.preprocessing_params[part])
    if cbx_sec_data:
        st.session_state.preprocessing_params[part] = True
        view_data.draw_source(1)
        view_data.draw_source_view(1)
        if '1' in st.session_state.data:
            st.write(st.session_state.data['1'])
            common_columns = list(set(st.session_state.data['0']).intersection(st.session_state.data['1']))

            if common_columns:
                #st.write("Merged on: " + str(common_columns))
                final_data = st.session_state.data['0'].merge(st.session_state.data['1'], how='left', on=common_columns)
                data_size = sys.getsizeof(final_data)
                if data_size > 209715200:
                    st.write('too large')
                    final_data = None
                else:
                    st.session_state.data['final'] = final_data
            else:
                st.write('no common columns found')
    else:
        st.session_state.preprocessing_params[part] = False
        if '1' in st.session_state.data_objects:
            st.session_state.data_objects.pop('1')
        if '1' in st.session_state.data:
            st.session_state.data.pop('1')


def draw_data_filter():
    part = 'data_filter'
    if part not in st.session_state.preprocessing_params:
        st.session_state.preprocessing_params[part] = True

    filter_expander = st.expander('Filter data', expanded=st.session_state.preprocessing_params[part])

    with filter_expander:
        col_selection, values = column_selection()
        st.session_state.preprocessing_params[col_selection] = values
        col_filters = column_filters()
        reset_preprocessing = st.button('Reset filters')
        if reset_preprocessing:
            reset_preprocessing_part()


def reset_preprocessing_part():
    st.session_state.preprocessing_params.pop('column_selection')
    st.session_state.preprocessing_params.pop('column_filter')
    st.experimental_rerun()


def draw_preprocessing():
    st.write('---')
    st.write("## Preprocessing")
    add_secondary_data()
    draw_data_filter()


