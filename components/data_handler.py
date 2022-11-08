import streamlit as st
import requests
import pandas as pd
import mysql.connector


@st.cache
def get_private_file(filename):
    github_session = requests.Session()
    github_session.auth = (st.secrets.github.user, st.secrets.github.pat)
    file = st.secrets.github.url + filename
    content = github_session.get(file).content.decode('utf-8')
    return content


@st.cache
def get_public_csv(filename):
    file = st.secrets.github.publicurl + filename
    df = pd.read_csv(file)
    return df


def run_private_code(filename):
    filename = "code/" + filename
    content = get_private_file(filename)
    code = compile(content, "<string>", "exec")
    return code


#@st.experimental_singleton
def connect_wp_db():
    return mysql.connector.connect(**st.secrets["wpmysql"])


#@st.experimental_memo(ttl=600)
def run_db_query(query):
    dbc = connect_wp_db()
    with dbc.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()
