import streamlit as st
import os
import sys

sys.path.append(os.getcwd())
from Backend.python.Database.db import authenticate_userlogin

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    
if "user_logged_in" not in st.session_state:
    st.session_state.user_logged_in = False
    
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

def login():
    
    with st.form("Login_Form"):
        lt1, lt2, lt3 = st.columns([1,1,1])
        with lt2:
            st.title("LOGIN", width = "stretch", text_alignment = "center")
        
        Username = st.text_input("username")
        Password = st.text_input("password", type="password")
    
        cl1, cl2, cl3 = st.columns([1,1,1])
        with cl2:
            if st.form_submit_button("Log in", width = "stretch"):
                if Username and Password:
                    if role := authenticate_userlogin(Username, Password):
                        if role == "USER":
                            st.session_state.logged_in = True
                            st.session_state.user_logged_in = True
                            st.rerun()
                        if role == "ADMIN":
                            st.session_state.logged_in = True
                            st.session_state.admin_logged_in = True
                            st.rerun()
                    else:
                        st.error("invalid username or password", width="stretch")
                else:
                    st.error("username and password can not be empty")
                

def logout():
    st.session_state.user_logged_in = False
    st.session_state.admin_logged_in = False
    st.toast("logged out!")
    st.rerun()
    
    

if st.session_state.user_logged_in:
    pg = st.navigation([
        st.Page("User/User.py", title="User", icon=":material/home:"),
        st.Page(logout, title="Log out", icon=":material/logout:")
    ])
    
elif st.session_state.admin_logged_in:
    pg = st.navigation([
        st.Page("Admin/Admin.py", title="Admin", icon=":material/home:"),
        st.Page(logout, title="Log out", icon=":material/logout:")
    ])
    
else:
    pg = st.navigation([
        st.Page(login, title="Log in", icon=":material/login:")
        ])
    
    
pg.run()
