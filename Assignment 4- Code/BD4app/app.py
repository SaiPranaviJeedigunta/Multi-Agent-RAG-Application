import streamlit as st
from pages.login import render as login_page
from pages.testing import render as testing_page

# Initialize session state variables
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# Navigation function
def navigate(page):
    st.session_state['page'] = page

def main():
    st.sidebar.title("Navigation")

    # Check if the user is logged in
    if st.session_state['logged_in']:
        # Sidebar navigation for logged-in users
        page_selection = st.sidebar.radio("Navigate to", ["Testing", "Logout"])

        if page_selection == "Testing":
            navigate("testing")
        elif page_selection == "Logout":
            st.session_state['logged_in'] = False
            navigate("login")
            st.experimental_rerun()  # Rerun the app after logging out
    else:
        navigate("login")

    # Page navigation logic
    if st.session_state['page'] == 'login':
        login_page()
    elif st.session_state['page'] == 'testing':
        testing_page()

if __name__ == "__main__":
    main()
