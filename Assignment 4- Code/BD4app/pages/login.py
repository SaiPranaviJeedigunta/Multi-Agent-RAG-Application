import streamlit as st

def render():
    # Page Title and Subheader with Styling
    st.markdown(
        "<h1 style='text-align: center; color: #00BFFF; font-size: 36px;'>🔐 Login to Your Account</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h4 style='text-align: center; color: #D3D3D3; font-size: 18px;'>Please enter your login credentials below</h4>",
        unsafe_allow_html=True
    )
    st.markdown("<hr style='border: 1px solid #4682B4;'>", unsafe_allow_html=True)

    # Centering form content
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Input fields for email and password
        email = st.text_input("📧 Email Address", placeholder="Enter your email", key="email")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password", key="password")

        # Placeholder for messages
        message_area = st.empty()

        # Simulate Login Button with local authentication
        if st.button("🔓 Login", help="Click to access your account"):
            # Dummy authentication logic (no backend integration)
            if email and password:
                # If both email and password are entered, simulate successful login
                st.session_state['logged_in'] = True
                st.session_state['page'] = "testing"
                st.write(f"🎉 Welcome back, {email}!")
            else:
                message_area.warning("⚠️ Please enter both email and password.")

    # Styling for the button and input fields
    st.markdown(
        """
        <style>
        div.stTextInput > label {
            font-size: 18px;
            color: #D3D3D3;
            font-weight: bold;
        }
        
        div.stButton > button:first-child {
            width: 100%;
            padding: 12px;
            font-size: 20px;
            font-weight: bold;
            background-color: #1E90FF;
            color: white;
            border: 2px solid #1E90FF;
            border-radius: 10px;
            transition: 0.3s;
        }
        
        div.stButton > button:first-child:hover {
            background-color: #32CD32;
            border-color: #32CD32;
            color: #FFFFFF;
        }
        
        input {
            background-color: #F0F8FF;
            color: #000000;
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #4682B4;
        }
        
        hr {
            border: 1px solid #4682B4;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown("<hr style='border: 1px solid #4682B4;'>", unsafe_allow_html=True)

# Render the login page when the script is run
if __name__ == "__main__":
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'

    # Navigation logic
    if st.session_state['logged_in']:
        st.session_state['page'] = 'testing'
    
    # Render the appropriate page based on the session state
    if st.session_state['page'] == 'login':
        render()
    elif st.session_state['page'] == 'testing':
        st.write("You are now on the testing page! 🎉")
