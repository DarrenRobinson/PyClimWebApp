# Streamlit tests
# https://docs.streamlit.io/develop/api-reference/app-testing


import streamlit.testing.v1


def test_app():
    app_test = streamlit.testing.v1.AppTest.from_file("app.py")

    app_test.run(timeout=10)

    assert not app_test.exception
