import streamlit as st
import folium
import sqlite3
import pandas as pd
from streamlit_folium import st_folium
from folium.plugins import LocateControl

#Create a local sqlite database 
conn = sqlite3.connect('data.db')

#Create a pandas dataframe for projects (project_id, project_name, lat, lon)
projects = pd.DataFrame({
    "project_id": ["P-000822"],
    "project_name": ["Port Nikau"],
    "lat": [-35.754596],
    "lon": [174.345201]
})

#Create a pandas dataframe to store project observations (project_id, observation_id, observation_date, lat, lon, observation)
observations = pd.DataFrame({
    "project_id": ["P-000822"],
    "observation_id": [1],
    "observation_datetime": ["2021-10-01 12:00:00"],
    "lat": [-35.754596],
    "lon": [174.345201],
    "observation": ["Groundwater seepage observed"]
})

#Write the dataframe to the database
projects.to_sql('projects', conn, if_exists='replace', index=False)
observations.to_sql('observations', conn, if_exists='replace', index=False)


st.session_state.project_id = None
c1, c2 = st.columns([0.7,0.3])

with c1:
    m = folium.Map(location=[-35.754596, 174.345201],zoom_start=18)
    LocateControl().add_to(m)
    st_data = st_folium(m)

    #If project is not select show marker for each project
    if st.session_state.project_id is None:
        for i, row in projects.iterrows():
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=row["project_id"],
                icon=folium.Icon(color="blue")
            ).add_to(m)

    #If project marker is clicked, set project_id to the selected project using session state
    if st_data.last_object_clicked_popup:
        project_id = st_data.last_object_clicked_popup
        st.session_state.project_id = project_id

    #Add a button to add new observation to the project with a cliked location on map
    if st.session_state.project_id:
        if st.button("Add Observation"):
            st.write("Add Observation")
            lat, lon = st_data.last_clicked
            st.write(f"Lat: {lat}, Lon: {lon}")
            observation = st.text_area("Observation")
            if st.button("Save"):
                observation_id = observations["observation_id"].max() + 1
                new_observation = pd.DataFrame({
                    "project_id": [project_id],
                    "observation_id": [observation_id],
                    "observation_datetime": ["2021-10-01 12:00:00"],
                    "lat": [lat],
                    "lon": [lon],
                    "observation": [observation]
                })
                new_observation.to_sql('observations', conn, if_exists='append', index=False)
                st.write("Observation saved")

with c2:
    st.write("Project Details")
    #select project from a dropdown
    if st.session_state.project_id is None: 
        project_id = st.selectbox("Select Project", projects["project_id"])
        st.session_state.project_id = project_id
    project = projects[projects["project_id"] == project_id]
    st.write(project)
    st.write("Observations")
    observations = pd.read_sql(f"SELECT * FROM observations WHERE project_id = '{project_id}'", conn)
    st.dataframe(observations)

    for i, row in observations.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=row["observation"],
            icon=folium.Icon(color="red")
        ).add_to(m)


    

