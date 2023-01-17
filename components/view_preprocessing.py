import streamlit as st
from . import session_state
from . import view_data
import wbdata
import pandas as pd
from pandas.api.types import is_numeric_dtype
import re
import sys
import numpy as np
from wordcloud import STOPWORDS
from textblob import Word


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


def draw_column_selection():
    st.write('Select columns:')
    group = 'column_selection'
    if group not in st.session_state.preprocessing_params:
        st.session_state.preprocessing_params[group] = list(st.session_state.data['final'].columns)
        columns = list(st.session_state.data['final'].columns)

    else:
        columns = st.session_state.preprocessing_params[group]
        columns[:] = [x for x in columns if (x in list(st.session_state.data['final'].columns))]

    with st.form('column_selection_form'):
        selected_columns = st.multiselect("Select columns", list(st.session_state.data['final'].columns),
                                          label_visibility="collapsed",
                                          default=columns)
        btn_update_columns = st.form_submit_button('Update columns')
    if btn_update_columns:
        st.session_state.preprocessing_params[group] = list(selected_columns)
    st.session_state.data['final'] = st.session_state.data['final'][selected_columns]


    return group, st.session_state.preprocessing_params[group]
    #st.session_state.preprocessing_params[group] = selected_columns
    #st.session_state.data['final'] = st.session_state.data['final'][selected_columns]
    #return group, selected_columns


def column_filters():
    st.write("Filter based on columns:")
    group = 'column_filter'
    if group not in st.session_state.preprocessing_params:
        #st.write('if')
        st.session_state.preprocessing_params[group] = {}
        cf_values = []
    else:
        #st.write('else')
        cf_values = list(st.session_state.preprocessing_params[group].keys())
        cf_values[:] = [x for x in cf_values if (x in st.session_state.data['final'].columns)]
        cf_values = list(cf_values)

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
                    st.session_state.preprocessing_params["column_selection"].append(list(st.session_state.data['1'].columns))
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
        filter_container = st.empty()
        with filter_container.container():
            col_selection, values = draw_column_selection()
            st.session_state.preprocessing_params[col_selection] = values
            col_filters = column_filters()
        reset_preprocessing = st.button('Reset filters')
        if reset_preprocessing:
            filter_container.empty()
            reset_preprocessing_part()


def reset_preprocessing_part():
    st.session_state.preprocessing_params.pop('column_selection')
    st.session_state.preprocessing_params.pop('column_filter')
    #st.session_state.preprocessing_params['data_filter'] = False
    st.experimental_rerun()


def calculate_column(data, first, operator, second):
    if operator == "+":
        column = data[first] + data[second]
    elif operator == "-":
        column = data[first] - data[second]
    elif operator == "*":
        column = data[first] * data[second]
    elif operator == "/":
        column = data[first] / data[second]
    return list(column)

def add_column():
    group = 'add_column'
    if group not in st.session_state.preprocessing_params:
        st.session_state.preprocessing_params[group] = {}
    else:
        columns = st.session_state.preprocessing_params[group]

    df = st.session_state.data['final'].copy()

    for key, value in st.session_state.preprocessing_params[group].items():
        new_column = calculate_column(df, value['first'], value['operator'], value['second'])
        col_name = value['name']
        # st.write(type(st.session_state.data['final']))
        df = st.session_state.data['final'].copy()
        df[col_name] = new_column
        # st.session_state.data['final']['test'] = new_column
        # st.write(df)
        st.session_state.data['final'] = df.copy()

    df = st.session_state.data['final'].copy()

    add_column_container = st.empty()
    with add_column_container.container():
        with st.form('add_column'):

            col1, col2, col3, col4, col5, col6 = st.columns([3,1,3,1,3,2])
            col1.write("New column name")
            col2.write('')
            col2.write('')
            col3.write('First column')
            col4.write('Operator')
            col5.write('Second column')
            col6.write('Delete')

            col_ind = 0
            new_columns = {}
            operators = ['+', '-', '*', '/']

            for key, value in st.session_state.preprocessing_params[group].items():
                col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 3, 1, 3, 2])
                new_columns[str(col_ind)] = {}
                new_columns[str(col_ind)]['name'] = col1.text_input('input name',
                                                                    label_visibility='collapsed',
                                                                    value=value['name'],
                                                                    key="inam" + str(col_ind))
                #new_columns[str(col_ind)] = col1.text_input('input name', label_visibility='collapsed',
                #
                #                                                    value=value['name'])
                col2.write('')
                col2.write('=')
                idx = (list(df.select_dtypes(include=[np.number]).columns)).index(value['first'])
                new_columns[str(col_ind)]['first'] = col3.selectbox('first column',
                                                                    df.select_dtypes(include=[np.number]).columns,
                                                                    index=idx,
                                                                    label_visibility="collapsed",
                                                                    key="fcol"+str(col_ind))
                idx = (operators.index(value['operator']))
                new_columns[str(col_ind)]['operator'] = col4.selectbox('operator',
                                                                    operators,
                                                                    index=idx,
                                                                    label_visibility="collapsed",
                                                                    key="ocol" + str(col_ind))
                idx = (list(df.select_dtypes(include=[np.number]).columns)).index(value['second'])
                new_columns[str(col_ind)]['second'] = col5.selectbox('second column',
                                                                    df.select_dtypes(include=[np.number]).columns,
                                                                    index=idx,
                                                                    label_visibility="collapsed",
                                                                    key="scol" + str(col_ind))

                new_columns[str(col_ind)]['delete'] = col6.checkbox('Delete',
                                                                    value=value['delete'],
                                                                    #label_visibility="collapsed",
                                                                    key="cbxdel" + str(col_ind))
                col6.write('')
                col_ind = col_ind + 1

            col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 3, 1, 3, 2])
            new_columns[str(col_ind)] = {}
            new_columns[str(col_ind)]['name'] = col1.text_input('input name', label_visibility='collapsed', placeholder='Enter new column name', key="inam" + str(col_ind))
            col2.write('')
            col2.write('=')

            idx = 0
            new_columns[str(col_ind)]['first'] = col3.selectbox('first column',
                                                                df.select_dtypes(include=[np.number]).columns,
                                                                index=idx,
                                                                label_visibility="collapsed",
                                                                key="fcol"+str(col_ind))

            idx2 = 0

            new_columns[str(col_ind)]['operator'] = col4.selectbox('operator',
                                                                   operators,
                                                                   index=idx2,
                                                                   label_visibility="collapsed",
                                                                   key="ocol" + str(col_ind))

            idx = 0
            new_columns[str(col_ind)]['second'] = col5.selectbox('second column',
                                                                 df.select_dtypes(include=[np.number]).columns,
                                                                 index=idx,
                                                                 label_visibility="collapsed",
                                                                 key="scol" + str(col_ind))

            #col6.write("")
            new_columns[str(col_ind)]['delete'] = col6.checkbox('Delete', key="cbxdel" + str(col_ind))

            btn_add_column = st.form_submit_button('Add columns')
        if btn_add_column:
            #st.write(new_columns)
            #complex = [src for src.value in new_columns.items() if not src.get('delete')]
            complex = {key: value for (key, value) in new_columns.items() if value['name'] != ""}
            complex = {key: value for (key, value) in complex.items() if not value['delete']}
            #complex = [src for src.value in complex.items() if src.get('name') == '']
            #st.write(complex)
            st.session_state.preprocessing_params[group] = complex
            st.experimental_rerun()



            #st.write(new_column)



            #add_column_container.empty()



def draw_column_manipulation():
    part = 'column_manipulation'
    if part not in st.session_state.preprocessing_params:
        st.session_state.preprocessing_params[part] = True
    filter_expander = st.expander('Manipulate columns', expanded=st.session_state.preprocessing_params[part])
    with filter_expander:
        add_column()

def draw_preprocessing():
    st.write('---')
    st.write("### Preprocessing")
    cat = st.session_state.data_type
    if cat == 'dataframe':
        add_secondary_data()
        draw_column_manipulation()
        draw_data_filter()
    elif cat == 'text':
        st.write("split and stuff, punctuation...")
        preprocess_text()


def preprocess_text():
    group = 'text_processing'
    if group not in st.session_state.preprocessing_params:
        st.session_state.preprocessing_params[group] = {
            'lowercase': True,
            'remove_punctuation': True,
            'remove_stopwords': True,
            'remove_rare': True,
            'lemmatize': True
        }
        options = st.session_state.preprocessing_params[group]
    else:
        options = st.session_state.preprocessing_params[group]
    df = st.session_state.data['final'].copy()
    with st.form('prep'):
        if st.checkbox('Convert to lower case', value=options['lowercase']):
            options['lowercase'] = True
            df['Text'] = df['Text'].apply(lambda x: " ".join(x.lower() for x in x.split()))
        else:
            options['lowercase'] = False

        if st.checkbox('Remove punctuation', value=options['remove_punctuation']):
            options['remove_punctuation'] = True
            df['Text'] = df['Text'].str.replace('[^\w\s]', '')
        else:
            options['remove_punctuation'] = False

        if st.checkbox('Remove stopwords', value=options['remove_stopwords']):
            options['remove_stopwords'] = True
            df['Text'] = df['Text'].apply(lambda x: " ".join(x for x in x.split() if x not in STOPWORDS))
        else:
            options['remove_stopwords'] = False

        if st.checkbox('Remove rare words (only one appearance)', value=options['remove_rare']):
            options['remove_rare'] = True
            freq = pd.Series(' '.join(df['Text']).split()).value_counts()
            less_freq = list(freq[freq == 1].index)
            df['Text'] = df['Text'].apply(lambda x: " ".join(x for x in x.split() if x not in less_freq))
        else:
            options['remove_rare'] = False

        if st.checkbox('Lemmatize', value=options['lemmatize']):
            options['lemmatize'] = True
            df['Text'] = df['Text'].apply(lambda x: " ".join([Word(word).lemmatize() for word in x.split()]))
        else:
            options['lemmatize'] = False



        btn_prep = st.form_submit_button('Update')
    if btn_prep:
        st.session_state.data['final'] = df.copy()
        st.session_state.preprocessing_params[group] = options

