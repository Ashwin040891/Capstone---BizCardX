import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
import mysql.connector as sql
import requests
from PIL import Image
import easyocr
import cv2
import re
import time

def set_page_config():
    st.set_page_config(
        page_title="BizCardX: Extracting Business Card Data with OCR",
        page_icon="https://uxwing.com/wp-content/themes/uxwing/download/business-professional-services/address-card-icon.png",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={'About': """# This OCR app is created by *Ashwin*!"""}
    )

set_page_config()

st.markdown("<h1 style='text-align: center; color:Indigo ;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

def setting_bg():
    st.markdown(f""" <style>.stApp {{
                        background:url("https://wallpapers.com/images/featured/plain-zoom-background-d3zz0xne0jlqiepg.jpg");
                        background-size: cover}}
                     </style>""", unsafe_allow_html=True)

setting_bg()

def upload_data():
    
    sql = "insert into card_data(name, designation, company, contact, email, website, address, city, state, pincode, image)"\
          "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    value = (m_name, m_designation, m_company, m_phone, m_mail_id, m_URL, m_Address, m_city, m_state, m_pincode, file_bytes)
    mycursor.execute(sql, value)
    mydb.commit()
    st.success('Above Data Successfully Uploaded to Database',icon="☑️")
    st.success("If you're not satisfied with above data, please navigate to 'Modify Data' tab to modify")
    
mydb = sql.connect(host="localhost",
                   user="root",
                   password="12345678",
                   database= "d102"
                  )
mycursor = mydb.cursor(buffered=True)

selected = option_menu(None, ["Home", "Upload & Extract", "Modify Data"],
                       icons=["house", "cloud-upload", "pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "25px", "text-align": "center", "margin": "0px",
                                            "--hover-color": "#6495ED"},
                               "icon": {"font-size": "35px"},
                               "container": {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#93cbf2"}})

if selected == 'Home':
    left, right = st.columns(2)
    with right:
        st.write('### Technologies Used')
        st.write('### *:red[Python]  *:red[Streamlit] *:red[EasyOCR] *:red[OpenCV] *:red[MySQL]')
        st.write("### How easyOCR works?")
        st.write("### 1. Feature Extraction - Create a set of features that can be used for additional analysis")
        st.write("### 2. Sequence Labeling - Uses LSTM networks to interpret the extracted features' sequential context")
        st.write("### 3. Decoding - Transcribes the labeled sequqnces into actual recognized texts")
        st.write("### *To Learn more about easyOCR [click here](https://pypi.org/project/easyocr/)")

    with left:
        st.markdown("### Welcome to the Business Card Application!")
        st.markdown('### Bizcard is a Python application designed to extract information from business cards. It utilizes various technologies to achieve this functionality.')
        st.write('### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')
        
if selected=='Upload & Extract':
    file, text = st.columns([3,2.5])
    with file:
        uploaded_file = st.file_uploader("Upload an image of a business card", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            #interprets a buffer as a 1-D array
            nparr = np.frombuffer(file_bytes, np.uint8)
            #reads image data from memory cache and converts into image format. this is generally used for loading the image efficiently from the internet
            #nparr - image data in bytes
            #specifies the way in which the image should be read
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            st.image(image, channels='BGR', use_column_width=True)

    with text:
        st.markdown("###### *After uploading image, press 'Extract & Upload' button for extracting text from image and uploading to database*")
        if st.button('Extract & Upload'):
            if image is not None:
                with st.spinner('Extracting & Uploading...'):
                    reader = easyocr.Reader(['en'])
                    results = reader.readtext(image)
                    print(results)
                    card_info = [i[1] for i in results]
                    print(card_info)
                    card = ' '.join(card_info)
                    replacement =[
                        (",",""),
                        (',',''),
                        ("WWW ", "www."),
                        ("www ", "www."),
                        ('www', 'www.'),
                        ('www.', 'www'),
                        ('wwW', 'www'),
                        ('wWW', 'www'),
                        ('.com', 'com'),
                        ('com', '.com'),
                    ] 
                    for old, new in replacement:
                        card = card.replace(old,new)
                    
                    ph_pattern = r"\+*\d{2,3}-\d{3}-\d{4}"
                    ph = re.findall(ph_pattern, card)
                    phone = ''
                    for i in ph:
                        phone = phone + ' ' + i
                        card =card.replace(i, '')
                    
                    mail_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}\b"
                    mail = re.findall(mail_pattern, card)
                    mail_id = ''
                    for ids in mail:
                        mail_id = mail_id + ids
                        card = card.replace(ids, '')
                    
                    url_pattern = r"www\.[A-Za-z0-9]+\.[A-Za-z]{2,3}"
                    url = re.findall(url_pattern,card)
                    URL = ''
                    for i in url:
                        URL = URL + i
                        card = card.replace(i,'')
                    
                    pin_pattern = r'\d+'
                    match = re.findall(pin_pattern, card)
                    pincode = ''
                    for i in match:
                        if len(i) == 6 or len(i) == 7:
                            pincode = pincode + i
                            card = card.replace(i,'')
                    
                    name_pattern = r'^[A-Za-z]+ [A-Za-z]+$|^[A-Za-z]+$|^[A-Za-z]+ & [A-Za-z]+$'
                    name_data = []
                    for i in card_info:
                        if re.findall(name_pattern, i):
                            if i not in 'WWW':
                                name_data.append(i)
                                card = card.replace(i, '')
                    name = name_data[0]
                    designation = name_data[1]
                    
                    if len(name_data)==3:
                        company = name_data[2]
                    else:
                        company = name_data[2]+' '+name_data[3]
                    card = card.replace(name,'')
                    card = card.replace(designation,'')
                    new = card.split()
                    if new[4] == 'St':
                        city = new[2]
                    else:
                        city = new[3]
                    if new[4] == 'St':
                        state = new[3]
                    else:
                        state = new[4]
                    if new[4] == 'St':
                        s = new[2]
                        s1 = new[4]
                        new[2] = s1
                        new[4] = s
                        Address = new[0:3]
                        Address = ' '.join(Address)
                    else:
                        Address = new[0:3]
                        Address = ' '.join(Address)
                        
                    st.write('')
                    print(st.write('##### :red[Name]       :',name))
                    print(st.write('##### :red[Designation]:',designation))
                    print(st.write('##### :red[Company]    :',company))
                    print(st.write('##### :red[Phone]      :',phone))
                    print(st.write('##### :red[email-ID]   :',mail_id))
                    print(st.write('##### :red[URL]        :',URL))
                    print(st.write('##### :red[Address]    :',Address))
                    print(st.write('##### :red[City]       :',city))
                    print(st.write('##### :red[State]      :',state))
                    print(st.write('##### :red[Pincode]    :',pincode))
                    
                    sql = "insert into card_data(name, designation, company, contact, email, website, address, city, state, pincode, image)"\
                        "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    value = (name, designation, company, phone, mail_id, URL, Address, city, state, pincode, file_bytes)
                    mycursor.execute(sql, value)
                    mydb.commit()
                    st.success('Above Data Successfully Uploaded to Database',icon="☑️")
                    st.success("If you're not satisfied with above data, please navigate to 'Modify Data' tab to modify")

if selected=='Modify Data':
        with st.spinner('Connecting...'):
            time.sleep(1)
        option = option_menu(None, ['Image data', "Update data", "Delete data"],
                             icons = ["image", "pencil-fill", 'exclamation-diamond'], orientation="horizontal", default_index=0)

        if option=='Image data':
            left, right = st.columns([2, 2.5])
            with left:
                mycursor.execute("select name from card_data")
                rows = mycursor.fetchall()
                row_name = [row[0] for row in rows]
                selection_name = st.selectbox("Select name", row_name)
                sql = "select distinct designation from card_data where name = %s"
                mycursor.execute(sql, (selection_name,))
                rows1 = mycursor.fetchall()
                row_designation = [row1[0] for row1 in rows1]
                selection_designation = st.selectbox("Select designation", row_designation)
                
                if st.button('Show Image'):
                    with right:
                        sql = "select image from card_data where name = %s and designation = %s"
                        mycursor.execute(sql, (selection_name, selection_designation))
                        result = mycursor.fetchone()
                        if result is not None:
                            image_data = result[0]
                            nparr = np.frombuffer(image_data, np.uint8)
                            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                            st.image(image, channels="BGR", use_column_width=True)
                        if result is None:
                            st.error("Image not found for the given name and designation.")
        
        if option=='Update data':
            name, new_name = st.columns(2)
            with name:
                mycursor.execute("select name from card_data")
                rows = mycursor.fetchall()
                row_name = [row[0] for row in rows]
                selection_name = st.selectbox("Select name", row_name)
                    
                sql = "select distinct designation from card_data where name = %s"
                mycursor.execute(sql, (selection_name,))
                rows1 = mycursor.fetchall()
                row_designation = [row1[0] for row1 in rows1]
                selection_designation = st.selectbox("Select designation", row_designation)
                
                sql = "select name,designation,company,contact,email,website,address,city,state,pincode from card_data where name = %s and designation = %s limit 1"
                mycursor.execute(sql, (selection_name, selection_designation))
                myresult = mycursor.fetchall()
                df = pd.DataFrame(myresult, columns=['Name','Designation','Company','Contact','e-mail','Website','Address','City','State','Pincode'])
                df.set_index('Name', drop=True, inplace=True)
                st.dataframe(df.T, width=700)
            
            with new_name:
                mycursor.execute("show columns from card_data")
                columns = mycursor.fetchall()
                column_names = [i[0].title() for i in columns if i[0] not in ['id', 'image', 'name', 'designation']]

                selection = st.selectbox("Select specific column to update", column_names)
                
                sql = f"select {selection} from card_data where name = %s and designation = %s"
                mycursor.execute(sql, (selection_name, selection_designation))
                col_data = str(mycursor.fetchone())[2:-3]
                
                new_data = st.text_input(f"Enter the new {selection}", col_data)
                
                sql = f"update card_data set {selection} = %s where name = %s and designation = %s"

                if st.button("Update"):
                    mycursor.execute(sql, (new_data, selection_name, selection_designation))
                    mydb.commit()
                    st.success("Updated Successfully",icon="👆")

        if option=='Delete data':
            left, right = st.columns([2,2.5])
            with left:
                mycursor.execute("select name from card_data")
                rows = mycursor.fetchall()
                row_name = [row[0] for row in rows]
                selection_name = st.selectbox("Select name", row_name)
                sql = "select distinct designation from card_data where name = %s"
                mycursor.execute(sql, (selection_name,))
                rows1 = mycursor.fetchall()
                row_designation = [row1[0] for row1 in rows1]
                selection_designation = st.selectbox("Select designation", row_designation)
            with left:
                if st.button('Delete'):
                    sql = "delete from card_data where name = %s and designation = %s"
                    mycursor.execute(sql, (selection_name, selection_designation))
                    mydb.commit()
                    st.success('Deleted successfully',icon='✅')
