import components.session_state as session_state
import components.view_controller as view_controller
import streamlit as st


developing = st.secrets.dev['is_developing']


def run():
    session_state.init_app()
    if developing:
        session_state.set_session_state('user_id', 'developer')
        view_controller.init_app_view()
    else:
        view_controller.check_user_session()
    #if session_state.get_session_state('query_params')['embedded'][0] or developing:
    #    view_controller.init_app_view()
    #else:
    #    view_controller.init_login_view()


if __name__ == "__main__":
    run()
