import components.session_state as session_state
#import components.view_controller as view_controller
#import components.authentication as authentication
import streamlit as st


def run():
    session_state.init_app()
    #if authentication.check_sign_in():
    #    view_controller.init_app_view()
    #else:
    #    view_controller.init_login_view()
    st.title("new app, who dis?")


if __name__ == "__main__":
    run()
    
