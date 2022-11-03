import streamlit as st
import requests

st.title('Welcome to this placeholder app!')

github_session = requests.Session()
github_session.auth = (st.secrets.github.user, st.secrets.github.pat)

content = github_session.get(st.secrets.github.url).content

exec(content.decode('utf-8'))

run()
