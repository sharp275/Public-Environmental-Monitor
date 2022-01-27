#Obtain data from SDS011 and upload to InfluxDB Cloud and TagoIO

from sds011 import SDS011
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import requests

#########################################################
# USER-EDITABLE SETTINGS

# How often to measure and read data in minutes (integer between 0 and 30, 0 for continous):
measurement_period = 5

#SDS011 port connection
PORT = "/dev/ttyUSB0"

#InfluxDB Cloud settings
token = ""
org = ""
bucket = ""
InfluxDB_URL = ""
host = ""

#Tago.io settings
TAGO_DEVICE_TOKEN_STRING = ""

# END OF USER-EDITABLE SETTINGS



sds = SDS011(port=PORT)
sds.set_working_period(rate=measurement_period)#one measurment every x minutes offers decent granularity and at least a few years of lifetime to the SDS011

while (True):
    try:
        measurement = sds.read_measurement()

        #InfluxDB Cloud Logging
        with InfluxDBClient(url=InfluxDB_URL, token=token, org=org) as client:
            write_api = client.write_api(write_options=SYNCHRONOUS)
            data = f"env,host={host} pm2.5={measurement['pm2.5']:.1f},pm10={measurement['pm10']:.1f}"
            write_api.write(bucket, org, data)

        #Start Tago logging
        tago_url = "http://api.tago.io/data"
        tago_header = {"Content-type": "application/json","Device-Token":TAGO_DEVICE_TOKEN_STRING}
        try:
            payload = [0]*2;
            payload[0] = {"variable":"pm25","value":f"{measurement['pm2.5']:.1f}"}
            payload[1] = {"variable":"pm10","value":f"{measurement['pm10']:.1f}"}
            requests.post(tago_url, json=payload, headers=tago_header, timeout=2)

        except Exception as e:
            # An error has occurred, likely due to a lost internet connection, 
            # and the post has failed.
            # The program will retry with the next data release and will succeed 
            # if the internet reconnects.
            print("HTTP POST failed with the following error:")
            print(repr(e))
            print("The program will continue and retry on the next data output.")

    except KeyboardInterrupt:
            sds.__del__()
