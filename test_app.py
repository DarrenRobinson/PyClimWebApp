# Streamlit tests
# https://docs.streamlit.io/develop/api-reference/app-testing

import os
import streamlit.testing.v1


def test_app(path: str = None, timeout: int = None):
    path = path or os.getenv("STREAMLIT_APP_PATH", "app.py")
    timeout = int(timeout or os.getenv('STREAMLIT_TEST_TIMEOUT', 60))

    app_test = streamlit.testing.v1.AppTest.from_file(path)

    app_test.run(timeout=timeout)

    assert not app_test.exception
