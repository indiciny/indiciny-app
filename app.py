import components.session_state as session_state
import components.view_controller as view_controller


developing = False


def run():
    session_state.init_app()
    if session_state.get_session_state('signed_in') or developing:
        view_controller.init_app_view()
    else:
        view_controller.init_login_view()


if __name__ == "__main__":
    run()
