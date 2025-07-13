# Live Monitoring in Acadia National Park

This repository features a Flask web server which provides an API endpoint for Raspberry Pi
devices to post sensor data to, along with a webpage to display the data. The webpage also contains
a section for traffic data, which is obtained from `.csv` files. These files contain sensitive data
on real park traffic statistics, and have been excluded from this repository. An example file (`exampledata.csv`)
has been included for anyone running the webpage locally who wishes to see the file formatting and
data on the page.

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