# Live Monitoring in Acadia National Park

### [FULL GITHUB REPOSITORY](https://github.com/asabramson/sensor-hat-transmission)

This repository features a Flask web server which provides an API endpoint for Raspberry Pi
devices to post sensor data to, along with a webpage to display the data. The webpage also contains
a section for traffic data, which is obtained from `.csv` files. These files contain sensitive data
on real park traffic statistics, and have been excluded from this repository. An example file (`exampledata.csv`)
has been included for anyone running the webpage locally who wishes to see the file formatting and
data on the page. For more information on how to run with the example data, see the bottom of this documentation.

## About the Project
I, along with three additional student researchers from Worcester Polytechnic Institute (WPI) worked with
Acadia National Park to determine whether real-time data collection would be possible with the hope of
improving park management and visitor experience. Currently, the park uses Jamar TRAX Apollyon GPS tube
counters to survey traffic; these counters do not update live, a park ranger must travel to each counter
in-person to download the data. While we were unsuccessful in processing the data on the Raspberry Pi
devices (Jamar's propietary Windows-only software is required), we were able to transmit the data in a
post-processed state (into a `.csv`). This project serves as a proof-of-concept; transmission of data is
possible from a Raspberry Pi (in the case of this project: temperature, humidity, and pressure from a
Waveshare Sense HAT B), if the park were to upgrade the traffic counters to a model that allows data
processing on a Raspberry Pi, transmission from in the park to a visitor-accessible website
(such as this one) is fully possible. 

## Traffic Simulation
The traffic section of this website (the page loaded when first opening) displays a simulation of what a possible website
could look like in a real-world smart park. As mentioned previously, the TRAX traffic counters are not able to retrieve
data live; six of the eight locations in the park (Bass Harbor Head Lighthouse, Jordan Pond, Otter Cliff Road, Moore Road/Schoodic, 
Sieur de Monts, Seawall) had their data manually pulled into `.csv` files, which were then used to populate the day and month
graphs. In a real-world scenario, a large-enough quantity of data would be available to enable predictive analysis of monthly, 
daily, and even hourly traffic levels. This would replace the current graphs which show data from June 2025 (a month prior to 
the proof-of-concept presentation session).

The TRAX counters are configured by the park to count in hourly intervals, which are far too wide for a successful smart
park setup. Because of this, the live-updating table is based on a Poisson sample and is purely an estimated simulation. 
In a real-world scenario, a smart traffic counter would be able to not only count in 30 second intervals, but transmit
that information in real-time to the table. Similarly, the thresholds for the congestion labels ("No congestion", "Minimal
congestion", "Moderate congestion", "Heavy congestion") can be customized by the park per each unique location, the road hosting
the counter, or any other variables influencing congestion beyond the raw numbers.

## Setup & Documentation
When running locally, install each of the dependencies listed in `requirements.txt` using `pip`. To run the website,
use the following command (the port flag is not required, `flask` runs on port 5000 by default and is recommended, 
however, if you are using macOS, port 5000 blocks certain POST requests with a `403 Forbidden` error, use another
port like 8000 to avoid this):
```
flask run --port 8000
```
POST requests do not have to come from a Raspberry Pi, they can come from any device that can send HTTP requests. In
testing, the Raspberry Pi's used an AT command (`AT#HTTPSND`) to send the POST request. To send your own POST request,
send to the following route:
```
http://<your-IP>:8000/api/sensordata
```
If you are on an enterprise, university, or other higher-security network, your device's IP will not be findable by the
Raspberry Pi (or substitute device). To combat this, use an API gateway such as `ngrok` (their official documentation
found [here](https://ngrok.com/docs)). For our testing, we installed using `homebrew`. To replicate our tests, first
start the web server, and then boot up `ngrok` using the following command (the `scheme` flag forces HTTP over HTTPS,
which was favorable for testing with the AT command; change the port to whichever one used in the `flask run` command):
```
ngrok http --scheme=http 8000 --host-header="localhost:8000"
```

### TO RUN WITH `exampledata.csv`:
1. In `traffic.js`, change the list `LOCATIONS` to only `[7]`
2. In `traffic.html`, remove the Jinja2 loop and update `{{i+1}}` to `7`
3. Duplicate the `exampledata.csv` file, and name one `exampledata_in.csv` and the other `exampledata_out.csv` (NOTE: 
you can change the values for the in and outbound so the lines are differentiable, you can duplicate more files to represent more locations)