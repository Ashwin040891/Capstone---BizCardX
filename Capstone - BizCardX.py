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

mydb = sql.connect(host="localhost",
                   user="root",
                   password="12345678",
                   database= "d102"
                  )
mycursor = mydb.cursor(buffered=True)

#selected = option_menu(None, ["Home", "Upload & Extract", "Database", "Profile"],
selected = option_menu(None, ["Home", "Upload & Extract", "Database"],
                       icons=["house", "cloud-upload", "pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "25px", "text-align": "center", "margin": "0px",
                                            "--hover-color": "#6495ED"},
                               "icon": {"font-size": "35px"},
                               "container": {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#93cbf2"}})

text_process = st.expander("Text Processing", expanded=False)

if selected == 'Home':
    left, right = st.columns(2)
    with right:
        st.write('### Technologies Used')
        st.write('### *:red[Python]')
        st.write('### *:red[Streamlit]')
        st.write('### *:red[EasyOCR]')
        st.write('### *:red[OpenCV]')
        st.write('### *:red[MySQL]')
        st.write("### *To Learn more about easyOCR [click here](https://pypi.org/project/easyocr/) ")

    with left:
        st.markdown("### Welcome to the Business Card Application!")
        st.markdown('### Bizcard is a Python application designed to extract information from business cards. It utilizes various technologies to achieve this functionality.')
        st.write('### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')
        #st.write("### Click on the ****:red[Image to text]**** option to start exploring the Bizcard extraction.")
        
if selected=='Upload & Extract':
    file, text = st.columns([3,2.5])
    with file:
        uploaded_file = st.file_uploader("Choose an image of a business card", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            #interprets a buffer as a 1-D array
            nparr = np.frombuffer(file_bytes, np.uint8)
            #reads image data from memory cache and converts into image format. this is generally used for loading the image efficiently from the internet
            #nparr - image data in bytes
            #specifies the way in which the image should be read
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            st.image(image, channels='BGR', use_column_width=True)

            #if st.button('Text Bounding'):
            #    with st.spinner('Detecting text...'):
            #        time.sleep(1)
            #    #convert an image from one color space to another
            #    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            #    #assignment of pixel values in relation to the thresholds provided
            #    #each pixel is compared with the threshold  value - < - 0
            #    #                                                 - > - max(255)
            #    #segmentation technique - separating a foreground object from it's background
            #    #done on grayscale images
            #    new, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            #    #Contours - line joining all the points along the boundary of an image that are having the same intensity
            #    #         - shape analysis, finding the size of object and object detection
            #    #cv2.RETR_EXTERNAL - Contour retreival mode
            #    #cv2.CHAIN_APPROX_SIMPLE - Contour approximation method
            #    #'contours' --> list of all contours in the image
            #    contours, new = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            #    for i in contours:
            #        #min and max locations of contour in x and y --> defines the bounding box
            #        #min_x, max_y, max_x-min_x, max_y-min_y
            #        x, y, w, h = cv2.boundingRect(i)
            #        color = (0, 255, 0)
            #        #draws an approx rectangle around the binary image - highlight the regions of interest
            #        #start, end, color, thickness
            #        new = cv2.rectangle(image, (x, y), (x + w, y + h), color, 2)
            #    st.write('Compare the images')
            #    st.image(new, use_column_width=True)
            #    st.info('Image might be inaccurate detection of text', icon='ℹ️')
    with text:
        #left,right = st.tabs(['Undefined text extraction', 'Pre_defined text extraction'])
        #with left:
        #    st.markdown('##### *Here you can view an undefined text extraction using :red[easyOCR]* and this is advanced tool for random text extraction.')
        #    st.write("Please note: It will accept all image and further update will available soon!")
        #    if st.button('Random Extraction'):
        #        with st.spinner('Extracting text...'):
        #            reader = easyocr.Reader(['en'])
        #            results = reader.readtext(image)
        #            for i in results:
        #                st.write(i[1])
        #
        #with right:
        st.markdown("###### *After uploading image, press 'Extract & Upload' button for extracting text from image and uploading to database*")
        #st.write('Note: This tab only for *:blue[business card image]* alone. It will not process random image')
        if st.button('Extract & Upload'):
            if image is not None:
                with st.spinner('Extracting & Uploading...'):
                    reader = easyocr.Reader(['en'])
                    results = reader.readtext(image)
                    card_info = [i[1] for i in results]
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
                    
                    #col_1, col_2 = st.columns([4, 4])
                    #with col_1:
                    #    m_name = st.text_input('Name', name)
                    #    m_designation = st.text_input('Designation', designation)
                    #    m_company = st.text_input('Company', company)
                    #    m_phone = st.text_input('Phone', phone)
                    #    m_mail_id = st.text_input('Email', mail_id)
                    #
                    #with col_2:
                    #    m_URL = st.text_input('Website', URL)
                    #    m_Address = st.text_input('Address', Address)
                    #    m_city = st.text_input('City', city)
                    #    m_state = st.text_input('State', state)
                    #    m_pincode = st.text_input('Pincode', pincode)
                    #    
                    #st.write("Please click 'Upload' button after making changes if necessary")
                    #print("Before upload")
                    #
                    #upload = st.button("Upload")
                    #if upload:
                    sql = "insert into card_data(name, designation, company, contact, email, website, address, city, state, pincode, image)"\
                        "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                    #value = (m_name, m_designation, m_company, m_phone, m_mail_id, m_URL, m_Address, m_city, m_state, m_pincode, file_bytes)
                    value = (name, designation, company, phone, mail_id, URL, Address, city, state, pincode, file_bytes)
                    mycursor.execute(sql, value)
                    mydb.commit()
                    st.success('Above Data Successfully Uploaded to Database',icon="☑️")
        #else:
        #    st.error("Please upload image before attempting to extract and load")

navigation,text_process=st.columns([1.2, 4.55])
# Database :-
if selected=='Database':
        with st.spinner('Connecting...'):
            time.sleep(1)
        with navigation:
            option = option_menu(None, ['Image data', "Update data", "Delete data"],
                                 icons = ["image", "pencil-fill", 'exclamation-diamond'], default_index=0)
        
        mycursor.execute("select * from card_data")
        myresult = mycursor.fetchall()
        df = pd.DataFrame(myresult, columns=['id','name','designation','company','contact','email','website','address','city','state','pincode','image'])
        df.set_index('id', drop=True, inplace=True)
        #st.write(df)

        # showing the image for selected name and designation
        if option=='Image data':
            left, right = st.columns([2, 2.5])
            with left:
                mycursor.execute("select name, designation from card_data")
                rows = mycursor.fetchall()
                row_name = [row[0] for row in rows]
                row_designation = [row[1] for row in rows]
                selection_name = st.selectbox("Select name", row_name)
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
        
        elif option=='Update data':
            name, new_name = st.columns(2)
            with name:
                mycursor.execute("select name from card_data")
                rows = mycursor.fetchall()
                row_name = [row[0] for row in rows]
                #row_designation = [row[1] for row in rows]
                selection_name = st.selectbox("Select name to update", row_name)
                #selection_designation = st.selectbox("Select designation to update", row_designation)
                #print("**", selection_designation)
                
                sql = "select distinct designation from card_data where name = %s"
                mycursor.execute(sql, (selection_name,))
                rows1 = mycursor.fetchall()
                row_designation = [row1[0] for row1 in rows1]
                selection_designation = st.selectbox("Select designation to update", row_designation)
            
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

                #execute the query with the new values
                if st.button("Update"):
                    mycursor.execute(sql, (new_data, selection_name, selection_designation))
                    mydb.commit()
                    st.success("Updated Successfully",icon="👆")

        else:
            left, right = st.columns([2,2.5])
            with left:
                mycursor.execute("select name, designation from card_data")
                rows = mycursor.fetchall()
                row_name = [row[0] for row in rows]
                row_designation = [row[1] for row in rows]
                selection_name = st.selectbox("Select name to delete", row_name)
            with right:
                selection_designation = st.selectbox("Select designation to delete", row_designation)
            with left:
                if st.button('Delete'):
                    sql = "delete from card_data where name = %s and designation = %s"
                    mycursor.execute(sql, (selection_name, selection_designation))
                    mydb.commit()
                    st.success('Deleted successfully',icon='✅')

            #st.write('')
            #st.markdown('### Result')
            #st.write('To provide a user-friendly interface, Bizcard utilizes Streamlit, a Python framework for building interactive web applications. Users can upload business card images through the Streamlit interface, and the application will process the images, extract the information, and display it on the screen. The application also provides options to view, update, and analyze the extracted data directly from the database.')
            #st.info('The detected text on image might be inaccurate. Still application under development fixing bugs.There is lot to explore on easyOCR and openCV',icon='ℹ️')

# profile 
if selected == 'Profile':
    col1,col2 = st.columns([3,3],gap="medium")
    with col1:
        st.subheader(":white[BizCardX Extracting business card Data ]",divider='rainbow')
        st.markdown("""
                    <div style="text-align: justify; font-size: 30px;">
                        <h3 style="color: black;">The objective of this project is to:</h3>
                        <p style="font-size: 25px; text-align: justify;">
                            The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.
                        </p></div>""", unsafe_allow_html=True)
                # Create vertical space using empty containers
        st.markdown("### :gray[Name:  ] :blue[Ashwin Kumar]")
        st.markdown("### :violet[My Project GitHub link] ⬇️")
        github_url = "https://github.com/DineshDhamodharan24/BizCardX-Extracting-Business-Card-Data-with-OCR"
        button_color = "#781734"
        # Create a button with a hyperlink
        button_html = f'<a href="{github_url}" target="_blank"><button style="font-size: 16px; background-color: {button_color}; color: #fff; padding: 8px 16px; border: none; border-radius: 4px;">GitHub My Phonepe Project</button></a>'
        st.markdown(button_html, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### :gray[Email: ] dineshdin9600@gmail.com")
        st.markdown("### :violet[My LinkedIn] ⬇️")
        linkedin_url = "https://www.linkedin.com/in/dinesh-dhamodharan-2bbb9722b/"
        button_color = "#781734"
        button_html = f'<a href="{linkedin_url}" target="_blank"><button style="font-size: 16px; background-color: {button_color}; color: #fff; padding: 8px 16px; border: none; border-radius: 4px;">My LinkedIn profile</button></a>'
        st.markdown(button_html, unsafe_allow_html=True)