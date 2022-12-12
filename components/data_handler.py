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
#from StringIO import StringIO


def cd_dir(ftp, target_dir):
    if target_dir != "":
        try:
            ftp.cwd(target_dir)
        except IOError:
            cd_dir(ftp, "/".join(target_dir.split("/")[:-1]))
            ftp.mkd(target_dir)


@st.experimental_memo(ttl=3600, show_spinner=False)
def get_cached_item(params):
    # Check cache availability
    ftp = FTP(st.secrets.ftpcache.ftp_url, st.secrets.ftpcache.ftp_user, st.secrets.ftpcache.ftp_pw)
    target_dir = st.session_state.data_code.replace("/", "-").replace(".", "-")
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
            os.remove(f_name)
            #st.write(df)
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
        target_dir = st.session_state.data_code.replace("/", "-").replace(".", "-")
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
        #st.write('stored data: ' + f_name)


def custom_caching():
    cache_item = 'params'
    with FTP(st.secrets.ftpcache.ftp_url, st.secrets.ftpcache.ftp_user, st.secrets.ftpcache.ftp_pw) as ftp:
        dir = ftp.mlsd()
        #ftp.storbinary(f'STOR {state_name}', bio)
    #st.write('custom cache')
    #st.write(dir)

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
def run_private_code(filename):
    #def get_cached_item(params):
    #    st.write('hello')
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


def log_transaction(type, action):
    dbc = mysql.connector.connect(**st.secrets["tradb"]) #connect_transaction_db()
    sql = "INSERT INTO indiciny_transactions (user_id, timestamp, transaction_type, transaction_object) VALUES (%s, %s, %s, %s)"
    values = (st.session_state.userlogin, round(time.time()), type, action)
    cursor = dbc.cursor()
    cursor.execute(sql, values)
    dbc.commit()
