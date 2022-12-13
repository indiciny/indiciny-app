import streamlit as st
from . import session_state
import wbdata
import pandas as pd
from pandas.api.types import is_numeric_dtype
import re


def get_country_metadata():
    country_data = pd.DataFrame(wbdata.get_country())
    region = pd.DataFrame(list(country_data.region)).rename(columns={"value": 'Region'})[['Region']]
    adminregion = pd.DataFrame(list(country_data.adminregion)).rename(columns={"value": 'Admin region'})[['Admin region']]
    incomeLevel = pd.DataFrame(list(country_data.incomeLevel)).rename(columns={"value": 'Income level'})[['Income level']]
    lendingType = pd.DataFrame(list(country_data.lendingType)).rename(columns={"value": 'Lending type'})[['Lending type']]
    country_data = country_data.join(region).join(adminregion).join(incomeLevel).join(lendingType)
    country_data = country_data[['id', 'iso2Code', 'name', 'capitalCity', 'longitude', 'latitude', 'Region',
                                 'Admin region', 'Income level', 'Lending type']]
    country_data = country_data.rename(columns={"name": "Country name (wb)", "id": "3-letter ISO country code",
                                                "iso2Code": "2-letter ISO code", 'capitalCity': "Capital city",
                                                "longitude": "Longitude", "latitude": "Latitude"})
    return country_data


def update_data_filter(filters):
    filtered_data = st.session_state.data
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
    st.session_state.data = filtered_data


def set_preprocessing_param(group, name, value):
    #if group not in st.session_state.preprocessing_params:
    #    st.session_state.preprocessing_params[group] = {}
    st.session_state.preprocessing_params[group][name] = value


def recommendations():
    st.write("Recommendations:")
    group = 'recommendations'
    if group not in st.session_state.preprocessing_params:
        st.session_state.preprocessing_params[group] = {}
    # Country meta data
    name = 'country_meta'
    if name in st.session_state.preprocessing_params[group]:
        is_checked = st.session_state.preprocessing_params[group][name]
    else:
        is_checked = True
    if '3-letter ISO country code' in st.session_state.data.columns:
        country_label = "Country data detected. Enrich with meta data from World Bank?"
        enrich_country_meta = st.checkbox(country_label, value=is_checked)
        if enrich_country_meta:
            st.session_state.data = st.session_state.data.join(
                get_country_metadata().set_index('3-letter ISO country code'), on='3-letter ISO country code')
            set_preprocessing_param(group, name, True)
        else:
            set_preprocessing_param(group, name, False)
    elif 'Country' in st.session_state.data.columns:
        country_label = "Country data detected. Enrich with meta data from World Bank?"
        enrich_country_meta = st.checkbox(country_label, value=True)
        if enrich_country_meta:
            st.session_state.data = st.session_state.data.join(
                get_country_metadata().set_index('Country name (wb)'), on='Country')
            set_preprocessing_param(group, name, True)
        else:
            set_preprocessing_param(group, name, False)

def column_filters():
    st.write("Filter based on columns:")
    group = 'column_filter'
    if group not in st.session_state.preprocessing_params:
        st.session_state.preprocessing_params[group] = {}
        cf_values = []
    else:
        cf_values = list(st.session_state.preprocessing_params[group].keys())
        cf_values = list(set(cf_values).intersection(st.session_state.data.columns))

    filters = st.multiselect("Select data filters", st.session_state.data.columns,
                             label_visibility="collapsed",
                             key='data_filter_select',
                             default=cf_values)
    categorical = st.session_state.data.select_dtypes(include=['category', object]).columns
    columns_filtered = False
    if group in st.session_state.preprocessing_params:
        dfdict = st.session_state.preprocessing_params[group]
    #else:
    column_filter = st.session_state.preprocessing_params[group]
    #st.write(column_filter)

    dfdictnew = {}
    if len(filters) > 0:
        st.session_state['data_filters_form'] = st.form('thisform')
        with st.session_state['data_filters_form']:
            for dfilter in filters:
                if filters.index(dfilter) > 0:
                    st.write('---')
                #st.write(dfilter)
                if st.session_state.data[dfilter].name in categorical:

                    if st.session_state.data[dfilter].nunique(dropna=True) < 10:
                        if dfilter in column_filter:
                            #st.write(column_filter[dfilter]['filter'])
                            cfil = column_filter[dfilter]['filter']
                            columns_filtered = True
                        else:
                            cfil = st.session_state.data[dfilter].unique() #(dropna=True)

                        #st.write(cfil)
                        catfilters = st.multiselect("Select categories",
                                                    st.session_state.data[dfilter].unique(),
                                                    default=cfil)
                        dfdictnew[dfilter] = {'filter': catfilters, 'type': 'categories'}
                    else:
                        dstring = st.text_input("Enter text filter for: " + dfilter)
                        if dstring:
                            dfdictnew[dfilter] = {'filter': dstring, 'type': 'string'}
                elif is_numeric_dtype(st.session_state.data[dfilter]):
                    dmin = round(float(st.session_state.data[dfilter].dropna().min()))
                    dmax = round(float(st.session_state.data[dfilter].dropna().max()))
                    if (dmax - dmin) > 100:
                        dstep = round((dmax - dmin) / 10)
                    else:
                        dstep = 1
                    if dfilter in column_filter:
                        #st.write(column_filter[dfilter]['filter'])
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
            # session_state.save_persistent_state(True)
            st.write('update')
            # if columns_filtered:
            columns_filtered = False
            # st.session_state.data_filtered = True
            # st.write(dfdict)
            st.session_state.preprocessing_params[group] = dfdictnew
        update_data_filter(st.session_state.preprocessing_params[group])
            #st.write(dfdict)
            #st.session_state.preprocessing_params[group] = {}

            #


def draw_preprocessing():
    preprocess_expander = st.expander("Preprocessing", expanded=st.session_state.preprocessing_expanded)
    if preprocess_expander.expanded:
        st.session_state.preprocessing_expanded = True
        with preprocess_expander:
            recommendations()
            column_filters()


                    #st.experimental_rerun()
            #else:
                #st.session_state.data = st.session_state.original_data

    else:
        st.session_state.preprocessing_expanded = False
        session_state.save_persistent_state(False)

    #st.write(st.session_state.preprocessing_params)
