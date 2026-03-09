import streamlit as st
from streamlit_option_menu import option_menu
import sys
import os

sys.path.append(os.getcwd())
from Backend.python.DL_Model.train import get_verify

selected = option_menu(
    menu_title="USER PORTAL",
    options=["SIGNATURE VERIFY"],
    icons=["check-circle", "plus-circle", "arrow-repeat"],
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
)


with st.form("verify-form"):
    cus_ID = st.text_input("NIC", width = "stretch")
    uploaded_img = st.file_uploader("UPLOAD SIGNATURE IMAGE", width = "stretch", type=["png","jpg","jpeg"])
    st.divider()
    if st.form_submit_button("Verify", width = "stretch"):
        st.image(uploaded_img, width = "stretch")
        
        with st.spinner("Wait for it...", show_time=True):
            score, status = get_verify(cus_ID, uploaded_img)
            if status == True:
                st.success(f'Signature Verified! matched score - {score}', icon="✅")
            elif status == False:
                st.error(f'Signature Forged! matched score - {score}', icon="🚨")
            else:
                st.warning('Signature Verification Failed', icon="⚠️")


