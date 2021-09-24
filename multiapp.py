'''
This class is the framework of the web-app. 
It is called and run (instantiated) in app.py.
'''

import datetime
import streamlit as st
from apps.helpers.helper import Helper
from apps.helpers.ui_helper import UIHelper
from apps.helpers.epw_helper import EPWHelper
import streamlit.components.v1 as components


class MultiApp:
    def __init__(self):
        self.apps = []
        self.helper = Helper()
        self.ui = UIHelper() 
        self.epw = EPWHelper()

    # This method allows you to add features (script files) to the 'Select Feature' dropdown menu on the sidebar
    def add_app(self, title, file_title, func):
        self.apps.append({
            "title": title,
            "file_title": file_title, 
            "function": func
        })

    # This method starts the web-app
    def run(self):
        st.sidebar.write('# PyClim')
        # begin_time = datetime.datetime.now()
        # test_df = self.ui._get_db_df()
        # test_df = test_df.values.tolist()
        # st.dataframe(test_df)
        # test_df = test_df.T.to_dict()
        # st.write(datetime.datetime.now() - begin_time)
        # st.write(test_df)
        # options = [[1,2,3],[4,5,6],[7,8,9]]
        # selected = st.selectbox(
        #     'testing',
        #     test_df,
        #     format_func=lambda x: x[0]
        # )
        # st.write(selected)
        # st.write(self.ui.file_name)

        self.helper.features = self.apps                        # Inform helper of available features
        self.ui.advanced_search()                               # Display sorting/filtering functionalities
        self.epw.read_epw_f(self.ui.file_name['file_url'])      # Fetch the epw dataframe and header info 
        # self.epw.read_epw_f(self.ui.file_name[4])      # Fetch the epw dataframe and header info 

        st.sidebar.markdown(                                    
            "Latitude: "+str(self.epw.lat)+                     
            " Longitude: "+str(self.epw.longitude)+             
            "<br>Time Zone: "+str(self.epw.timezone), 
            unsafe_allow_html=True                              
        )
        st.sidebar.write("---")

        # Display feature selection dropdown
        app = st.sidebar.selectbox(
            'Analysis Tools:',
            self.apps,
            format_func=lambda app: app['title']
        )
        
        self.epw.epw_filter(app['file_title'])               # Filter dataset for selected feature if applicable
        # self.epw.epw_to_file_list()                          # Convert the epw dataframe to list format with first two rows as header info
        st.sidebar.write("---")
        app['function'](app, self.epw, self.ui)              # Run the selected feature script
        # Site analytics
        with st.sidebar:
            if app['file_title'] != 'intro':
                st.write("---")
            st.markdown('<center><a href="https://statcounter.com/p12570505/?guest=1" target="_blank">View Visitor Stats</a></center>', unsafe_allow_html=True)
            components.html("""
                <!-- Default Statcounter code for PyClim Web App
                https://share.streamlit.io/darrenrobinson/pyclimwebapp/main/app.py
                -->
                <center><script type="text/javascript">
                var sc_project=12570505; 
                var sc_invisible=0; 
                var sc_security="a197d8ba"; 
                var scJsHost = "https://";
                document.write("<sc"+"ript type='text/javascript' src='" +
                scJsHost+
                "statcounter.com/counter/counter.js'></"+"script>");
                </script></center>
                <noscript><div class="statcounter"><a title="free web stats"
                href="https://statcounter.com/" target="_blank"><img
                class="statcounter"
                src="https://c.statcounter.com/12570505/0/a197d8ba/0/"
                alt="free web stats"></a></div></noscript>
                <!-- End of Statcounter Code -->
            """)
            
