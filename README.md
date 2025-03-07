# PyClim

A series of Python modules, based around the matplotlib library, for the analysis of hourly weather data. It is intended as a resources for architectural / engineering / technology students and practitioners, to help develop early-stage bioclimatic design concepts.

PyClim is organised around the following modules

- ClimAnalFunctions: functions relating to solar geometry, psychrometry and illumination.

- Psychros: creates psychrometric charts for the plotting ot climate data {and of transformed data to mimic evaporative cooling}.

- SolarIrradiation_Aniso: creates solar irradiation surface plots of annual irradiation incident on a tilted plane solar collector.

- Sunpath: creates sunpath diagrams in stereographic projection; plotting time lines either according to solar or clock time; this latter representing the Analemma, calculated using the equation of time (EqT).

- SolarGeo_subplots: creates a 3x2 grid of subplots: the first three plotting daily variations in declination, EqT and solar daylength; the latter three plotting hourly solar altitude, azimuth and cosine of the angle of incidence on a collector.

- WeatherAnalysis: creates a range of plots and statistics of climate variables: 1) temporal solar irradiance / maps, 2) violin plots of key synoptic variables, 3) Monthly degree-day bar charts, 4) inverse illuminance cumulative distribution function: determines light switch-off hours, 5) wind speed / temperature frequency histograms, 6) ground temperature profile.

- WindRose: plots a user-controllable wind rose, with theta segments of azimuthal sectors falsecoloured either according to the hours that the wind approaches that direction and in the indicated (theta) speed, or at the indicated (theta) temperature.

# Development

Please read ["First steps building Streamlit apps"](https://docs.streamlit.io/get-started/tutorials) in their documentation.

Run the development instance at http://localhost:8502

```bash
streamlit run app.py
```

# Installation

See [`deploy.sh`](./deploy.sh) which is a deployment script that will install this app and the nginx web server.

```bash
sudo bash -x deploy.sh
```

# Usage

## Service control

Enable the service

```bash
sudo systemctl enable streamlit.service
```

Start the service

```bash
sudo systemctl start streamlit.service
```

# Configuration

For [Streamlit configuration](https://docs.streamlit.io/develop/api-reference/configuration/config.toml), edit `.streamlit/config.toml`.

# Monitoring

View the service status

```bash
sudo systemctl status nginx.service
sudo systemctl status streamlit.service
```

View service logs

```bash
sudo journalctl --follow -u streamlit.service
```

```bash
sudo journalctl -u nginx.service
```

Web server access logs

```bash
sudo tail -f /var/log/nginx/access.log
```

and error logs

```bash
sudo tail -f /var/log/nginx/error.log
```
