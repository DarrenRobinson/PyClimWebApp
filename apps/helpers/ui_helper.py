import streamlit as st
import base64
import io
# from io import BytesIO

# General naming convention:
# func(): methods to be called by user
# _func(): assisting methods called by system
class UIHelper():  
    def __init__(self):
        self._days_in_a_month()
    #
    # The following methods
    # (
    # _save_plt_fig, 
    # generate_fig_dl_link
    # )
    # are used for generating figure download links
    #

    # def _save_plt_fig(self, fig, filename, format):
    #     tmpfile = BytesIO()
    #     fig.savefig(tmpfile, format=format, dpi=300)
    #     encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
    #     href = '<a href=\'data:image/{};base64,{}\' download=\'{}\'>{}</a>'.format(format, encoded, filename+"."+format, format.upper())
    #     return href

    # def generate_fig_dl_link(self, fig, filename):
    #     formats = ['jpg', 'png', 'svg', 'pdf']
    #     links = []
    #     for format in formats:
    #         links.append(self._save_plt_fig(fig, filename, format))
    #     links_str = ' '.join(links)
    #     hrefs = '<center>Download figures '+links_str+'</center><br>'
    #     return hrefs
    
    def _fig_to_base64(self, figure, format):
        img = io.BytesIO()
        figure.savefig(img, format=format, dpi=300)
        img.seek(0)
        return base64.b64encode(img.getvalue())

    def base64_to_link_and_graph(self, figure, filename, format, width, height):
        decoded = self._fig_to_base64(figure, format).decode('utf-8')
        graph = '<img width={} height={} src="data:image/jpg;base64, {}">'.format(width, height, decoded)
        href = '<center>Download figure <a href=\'data:image/{};base64,{}\' download=\'{}\'>{}</a></center><br>'.format(format, decoded, filename+"."+format, format.upper())
        return graph, href

    # def format_selector(self):
    #     options = ['jpg', 'png', 'svg', 'pdf']
    #     file_format = st.sidebar.selectbox(
    #         "Figure format to download",
    #         options,
    #         index=0
    #     )
    #     return file_format
    #   





    #
    # The following methods
    # (
    # _session_keys_init, 
    # _days_in_a_month, 
    # _check_day, 
    # _check_start_day, 
    # _check_end_day,
    # time_filter
    # )
    # are used for displaying the time filter panel in psychros and WindRose
    #

    # This method generates a set of feature-specific names e.g. psychros_start_month, windrose_start_month
    # so that the time filter stores these parameters separately for each feature in st.session_state.
    def _session_keys_init(self, selected_feature):
        if 'session_keys' not in st.session_state:
            st.session_state['session_keys'] = {}
        st.session_state['session_keys']['start_month'] = selected_feature+"_start_month"
        st.session_state['session_keys']['end_month'] = selected_feature+"_end_month"
        st.session_state['session_keys']['start_day'] = selected_feature+"_start_day"
        st.session_state['session_keys']['end_day'] = selected_feature+"_end_day"
        st.session_state['session_keys']['start_hour'] = selected_feature+"_start_hour"
        st.session_state['session_keys']['end_hour'] = selected_feature+"_end_hour"

    # This method generates a set of number arrays for days in different months (e.g. for start and end day dropdowns)
    def _days_in_a_month(self):
        self.days = [0] * 12
        for i in range(1,13):
            if i in [1, 3, 5, 7, 8, 10, 12]:
                self.days[i-1] = list(range(1,32))
            elif i == 2:
                self.days[i-1] = list(range(1,29))
            else:
                self.days[i-1] = list(range(1,31))

    # _check_day, _check_start_day, _check_end_day are callbacks from start_month and end_month dropdowns.
    def _check_day(self, start_or_end):    
        day = st.session_state['session_keys'][start_or_end+'_day']
        month = st.session_state['session_keys'][start_or_end+'_month']
        if (day in st.session_state) & (month in st.session_state):
            # If the previously selected day exceeded the day range in the newly selected month, it's reset to 1.
            if st.session_state[day] > (len(self.days[ st.session_state[month]['value']-1 ])): 
                st.session_state[day] = 1  

    # This is the main method to display the time filter dropdowns.
    def time_filter(self, feature):
        self._session_keys_init(feature)
        months = [
            {"title": "January", "value": 1}, 
            {"title": "February", "value": 2}, 
            {"title": "March", "value": 3}, 
            {"title": "April", "value": 4}, 
            {"title": "May", "value": 5}, 
            {"title": "June", "value": 6}, 
            {"title": "July", "value": 7}, 
            {"title": "August", "value": 8}, 
            {"title": "September", "value": 9}, 
            {"title": "October", "value": 10}, 
            {"title": "November", "value": 11}, 
            {"title": "December", "value": 12}
        ]
        start_day = st.session_state['session_keys']['start_day']
        end_day = st.session_state['session_keys']['end_day']
        start_month = st.session_state['session_keys']['start_month']
        end_month = st.session_state['session_keys']['end_month']
        start_hour = st.session_state['session_keys']['start_hour']
        end_hour = st.session_state['session_keys']['end_hour']

        # Set the dropdowns to display the previously selected month if applicable
        start_month_index = st.session_state[ start_month ]['value']-1 if start_month in st.session_state else 0
        end_month_index = st.session_state[ end_month ]['value']-1 if end_month in st.session_state else 11

        # Set the day range according to the month selected 
        start_days = self.days[ start_month_index ]
        end_days = self.days[ end_month_index ]
        
        # Set the dropdowns to display the previously selected day if applicable
        start_day_index = st.session_state[ start_day ]-1 if start_day in st.session_state else 0
        end_day_index = st.session_state[ end_day ]-1 if end_day in st.session_state else end_days.index(max(end_days))
        
        # Set the dropdowns to display the previously selected hour if applicable
        start_hour_index = st.session_state[ start_hour ]-1 if start_hour in st.session_state else 0
        end_hour_index = st.session_state[ end_hour ]-1 if end_hour in st.session_state else 23

        # Dropdowns
        col1, col2 = st.sidebar.columns(2)
        col2.selectbox(
            "Start Month", 
            months, 
            format_func=lambda months: months['title'], 
            key=start_month, 
            index = start_month_index, 
            help="This filter controls the range of data points that are plotted",
            on_change=self._check_day,
            args=['start']
        )
        col2.selectbox(
            "End Month", 
            months, 
            format_func=lambda months: months['title'], 
            key=end_month, 
            index = end_month_index, 
            help="This filter controls the range of data points that are plotted",
            on_change=self._check_day,
            args=['end']
        )
        col1.selectbox(
            "Start Day", 
            start_days, 
            key=start_day, 
            index = start_day_index,
            help="This filter controls the range of data points that are plotted"
        )
        col1.selectbox(
            "End Day", 
            end_days, 
            key=end_day, 
            index = end_day_index, 
            help="This filter controls the range of data points that are plotted"
        )
        col1.selectbox(
            "Start Hour", 
            list(range(1,25)), 
            key=start_hour, 
            index = start_hour_index, 
            help="This filter controls the range of data points that are plotted"
        )
        col2.selectbox(
            "End Hour",
            list(range(1,25)), 
            key=end_hour, 
            index = end_hour_index, 
            help="This filter controls the range of data points that are plotted"
        )    
        
        # Display text underneath title to indicate the range of filtered data currently showing
        if (end_hour_index >= start_hour_index):
            show_hour = str(start_hour_index+1)+":00 to "+str(end_hour_index+1)+":00,"
        else:
            show_hour = "1:00 to "+str(end_hour_index+1)+":00 and "+str(start_hour_index+1)+":00 to 24:00,"
        
        if (
            (end_month_index > start_month_index) 
            | 
            ((end_month_index == start_month_index) & (end_day_index >= start_day_index))
        ):
            st.write(
                "Showing:", 
                show_hour, 
                str(start_day_index+1), 
                months[start_month_index]['title'], 
                "to", 
                str(end_day_index+1), 
                months[end_month_index]['title']
            )
        else:
            st.write(
                "Showing:", 
                show_hour, 
                "1", 
                months[0]['title'], 
                "to", 
                str(end_day_index+1), 
                months[end_month_index]['title'], 
                "and", 
                str(start_day_index+1), 
                months[start_month_index]['title'], 
                "to 31", 
                months[-1]['title']
            )




    # This method helps with display decisions. It checks if any time filter parameters i.e. month, day & hour are different from default.
    def is_filter_applied(self, feature):
        time_var = {'start_month': 1, 'start_day': 1, 'end_month': 12, 'end_day': 31, 'start_hour': 1, 'end_hour': 24}
        for var in time_var.keys():
            if feature+"_"+var in st.session_state:
                if (var == 'start_month') | (var == 'end_month'):
                    if st.session_state[feature+"_"+var]['value'] != time_var[var]:
                        return True
                elif st.session_state[feature+"_"+var] != time_var[var]:
                    return True
        return False