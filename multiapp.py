'''
This class is the framework of the web-app. 
It is called and run (instantiated) in app.py.
'''

import streamlit as st
from apps.helpers.helper import Helper
from apps.helpers.ui_helper import UIHelper
from apps.helpers.epw_helper import EPWHelper
import streamlit.components.v1 as components

class MultiApp:
    def __init__(self):
        self.apps = []

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

        helper = Helper()
        ui = UIHelper() 
        epw = EPWHelper()

        # Inform helper of available features
        helper.features = self.apps   

        # Display sorting/filtering functionalities                
        ui.advanced_search()   
            
        if 'epw_valid' not in st.session_state:
            st.session_state['epw_valid'] = True

        try:
            # Fetch the epw dataframe and header info
            epw.read_epw_f(ui.file_name['file_url'])     
        except:
            st.session_state['epw_valid'] = False
        else:
            if epw.dataframe.empty:
                st.session_state['epw_valid'] = False
            
        if st.session_state['epw_valid']:
            st.sidebar.markdown(                                    
                "Latitude: "+str(st.session_state['lat'])+                     
                " Longitude: "+str(st.session_state['longitude'])+             
                "<br>Time Zone: "+str(st.session_state['timezone']), 
                unsafe_allow_html=True                              
            )

            st.sidebar.write("---")

            # Display feature selection dropdown
            app = st.sidebar.selectbox(
                'Analysis Tools:',
                self.apps,
                format_func=lambda app: app['title']
            )

            # Filter dataset if applicable
            if (app['file_title'] == 'windrose') or (app['file_title'] == 'psychros'):
                epw.epw_filter(app['file_title'])             
            
            st.sidebar.write("---")

            # Run the selected feature script
            app['function'](app, epw, ui)                       

            # Site analytics
            with st.sidebar:
                st.write("---") if app['file_title'] != 'intro' else None
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
        else:
            st.error('Unable to read the selected epw file')
