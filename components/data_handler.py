import streamlit as st
import requests
import pandas as pd
import mysql.connector
import time
from ftplib import FTP
import io
from dateutil import parser
import datetime
import os


#@st.experimental_memo(ttl=3600, show_spinner=False)
def get_states(directory):
    ftp = FTP(st.secrets.ftp.ftp_url, st.secrets.ftp.ftp_user, st.secrets.ftp.ftp_pw)
    try:
        ftp.cwd(directory)
    except:
        ftp.mkd(directory)
        ftp.cwd(directory)
    files = ftp.nlst()
    return files


def delete_files(directory, file):
    ftp = FTP(st.secrets.ftp.ftp_url, st.secrets.ftp.ftp_user, st.secrets.ftp.ftp_pw)
    ftp.cwd(directory)
    ftp.delete(file)


@st.experimental_memo(ttl=3600, show_spinner=False)
def get_cached_item(params):
    # Check cache availability
    ftp = FTP(st.secrets.ftpcache.ftp_url, st.secrets.ftpcache.ftp_user, st.secrets.ftpcache.ftp_pw)
    target_dir = st.session_state.data_objects[st.session_state.data_index]['data_code'].replace("/", "-").replace(".", "-")
    try:
        ftp.cwd(target_dir)
    except:
        ftp.mkd(target_dir)
        ftp.cwd(target_dir)
    f_name = ''
    for i in params.values():
        f_name += i.replace(" ", "-")
    if f_name != "":
        found_file = False
        f_name = f_name + ".csv"
        with open(f_name, "wb") as file:
            if f_name in ftp.nlst():
                timestamp = ftp.voidcmd(f"MDTM {f_name}")[4:].strip()
                mod_time = parser.parse(timestamp)
                cutoff_date = (datetime.datetime.today() - datetime.timedelta(days=7))
                if mod_time > cutoff_date:
                    ftp.retrbinary(f"RETR {f_name}", file.write)
                    found_file = True
                else:
                    #st.sidebar.warning('cache miss: ' + f_name)
                    found_file = False
        if found_file:
            #st.sidebar.success('cache hit: ' + f_name)
            df = pd.read_csv(f_name)
            try:
                os.remove(f_name)
            except:
                pass
            return df
    else:
        return None


def store_cached_item(params, data):
    f_name = ''
    for i in params.values():
        f_name += i.replace(" ", "-")
    if f_name != "":
        f_name = f_name + ".csv"
        ftp = FTP(st.secrets.ftpcache.ftp_url, st.secrets.ftpcache.ftp_user, st.secrets.ftpcache.ftp_pw)
        target_dir = st.session_state.data_objects[st.session_state.data_index]['data_code'].replace("/", "-").replace(".", "-")
        try:
            ftp.cwd(target_dir)
        except:
            ftp.mkd(target_dir)
            ftp.cwd(target_dir)

        buffer = io.StringIO()
        data.to_csv(buffer, index=False)
        text = buffer.getvalue()
        bio = io.BytesIO(str.encode(text))
        ftp.storbinary(f'STOR {f_name}', bio)
        try:
            os.remove(f_name)
        except:
            pass
        st.experimental_memo.clear()
        #st.write('stored data: ' + f_name)


#@st.experimental_memo
def get_private_file(filename):
    github_session = requests.Session()
    github_session.auth = (st.secrets.github.user, st.secrets.github.pat)
    file = st.secrets.github.url + filename
    content = github_session.get(file).content.decode('utf-8')
    return content


@st.experimental_memo
def get_public_csv(filename):
    file = st.secrets.github.publicurl + filename
    df = pd.read_csv(file)
    return df


#@st.experimental_memo
def run_private_code(filename, data_index):
    if data_index is not None:
        st.session_state.data_index = data_index
    filename = "code/" + filename
    content = get_private_file(filename)
    code = compile(content, "<string>", "exec")
    exec(code)


@st.experimental_singleton
def connect_wp_db():
    return mysql.connector.connect(**st.secrets["wpmysql"])


#@st.experimental_singleton
def connect_transaction_db():
    return mysql.connector.connect(**st.secrets["tradb"])

#@st.experimental_memo(ttl=600)
def run_db_query(query):
    dbc = connect_wp_db()
    with dbc.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def log_transaction(type):
    dbc = mysql.connector.connect(**st.secrets["tradb"]) #connect_transaction_db()
    sql = "INSERT INTO indiciny_transactions (user_id, transaction_type, data_source, data_method) VALUES (%s, %s, %s, %s)"
    do = []
    if st.session_state.data_objects:
        for key, data in st.session_state.data_objects.items():
            do.append(data['data_code'])
        dc = ', '.join(do)
    else:
        dc = ''
    ao = []
    if st.session_state.analysis_objects:
        for key, data in st.session_state.analysis_objects.items():
            ao.append(data['analysis_code'])
        ac = ', '.join(ao)
    else:
        ac = ''
    values = (st.session_state.uid, type, dc, ac)
    cursor = dbc.cursor()
    cursor.execute(sql, values)
    dbc.commit()
