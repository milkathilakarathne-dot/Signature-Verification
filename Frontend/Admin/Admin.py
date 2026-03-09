import streamlit as st
import os
import sys
from streamlit_option_menu import option_menu

sys.path.append(os.getcwd())
from Backend.python.DL_Model.train import get_verify, Model_train, add_new_data


if "model_train" not in st.session_state:
    st.session_state.model_train = False


selected = option_menu(
    menu_title="ADMIN PORTAL",
    options=["VERIFY", "ADD NEW", "RETRAIN MODEL"],
    icons=["check-circle", "plus-circle", "arrow-repeat"],
    menu_icon="cast", 
    default_index=0, 
    orientation="horizontal",
)

if selected == "VERIFY":
    
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
                    st.warning('something went wrong', icon="⚠️")
    

elif selected == "ADD NEW":
    with st.form("verify-form"):
        customerID = st.text_input("CUSTOMER NIC", width = "stretch")
        uploaded_img = st.file_uploader("UPLOAD SIGNATURE IMAGE", accept_multiple_files = True, width = "stretch", type=["png","jpg","jpeg"])
        st.divider()
        if st.form_submit_button("Add New", width = "stretch"):
        
            img_name = add_new_data(customerID, uploaded_img)
            if img_name:
                st.toast(f'Signature images saved as {img_name} under {customerID}', icon="✅")
            else:
                st.warning('Signature images adding process failed', icon="⚠️")
                


elif selected == "RETRAIN MODEL":
    st.divider()
    st.markdown("""<div style='text-align: center; font-size: 12px; color: white;'> Click here to Retrain Signature model with new data </div>""",unsafe_allow_html=True)
    
    cl1, cl2, cl3 = st.columns([1,1,1])
    with cl2:
        if st.button("Retrain", width = "stretch"):
            st.session_state.model_train = True
            


    if st.session_state.model_train:
        
        with st.spinner("Training...", show_time=True):
            status = Model_train()
        
            if status == True:
                st.success('Model trained & saved for new Data', icon="✅")
                st.balloons()
                st.session_state.model_train = False
            else:
                st.warning('Model training process failed!', icon="⚠️")
                st.session_state.model_train = False
