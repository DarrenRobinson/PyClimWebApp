import streamlit as st
from streamlit_folium import folium_static
import folium

"# streamlit-folium"

with st.echo():
    import streamlit as st
    from streamlit_folium import folium_static
    import folium

    # center on Liberty Bell
    m = folium.Map(location=[39.949610, -75.150282], zoom_start=1)

    # add marker for Liberty Bell
    tooltip = "http://google.com"
    folium.Marker(
        [39.949610, -75.150282], popup='<a href="http://google.com" target="_self">link</a>', tooltip=tooltip
    ).add_to(m)

    # call to render Folium map in Streamlit
    folium_static(m)

    