#  log_data_to_InfluxDB.py
   
#  Example for logging data to InfluxDB Cloud and Tago.IO for the Metriful MS430. 
#  This example is designed to run with Python 3 on a Raspberry Pi and based on
#  the example provided by Metriful Ltd.
   
#  Copyright 2020 Metriful Ltd. 
#  Licensed under the MIT License - for further details see LICENSE.txt

from sensor_package.sensor_functions import *
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import requests

#########################################################
# USER-EDITABLE SETTINGS

# How often to measure and read data (every 3, 100, or 300 seconds):
cycle_period = CYCLE_PERIOD_100_S 

#InfluxDB Cloud settings
token = ""
org = ""
bucket = ""
InfluxDB_URL = ""
host = ""

#Tago.io settings
TAGO_DEVICE_TOKEN_STRING = ""

# END OF USER-EDITABLE SETTINGS
#########################################################

# Set up the GPIO and I2C communications bus
(GPIO, I2C_bus) = SensorHardwareSetup()

# Apply the chosen settings to the MS430
I2C_bus.write_i2c_block_data(i2c_7bit_address, PARTICLE_SENSOR_SELECT_REG, [PARTICLE_SENSOR])
I2C_bus.write_i2c_block_data(i2c_7bit_address, CYCLE_TIME_PERIOD_REG, [cycle_period])

#########################################################

print("Entering cycle mode and waiting for data. Press ctrl-c to exit.")

# Enter cycle mode
I2C_bus.write_byte(i2c_7bit_address, CYCLE_MODE_CMD)

while (True):

  # Wait for the next new data release, indicated by a falling edge on READY
  while (not GPIO.event_detected(READY_pin)):
    sleep(0.05)

  # Air data
  # Choose output temperature unit (C or F) in sensor_functions.py
  air_data = get_air_data(I2C_bus)
  
  # Air quality data
  # The initial self-calibration of the air quality data may take several
  # minutes to complete. During this time the accuracy parameter is zero 
  # and the data values are not valid.
  air_quality_data = get_air_quality_data(I2C_bus)
    
  # Light data
  light_data = get_light_data(I2C_bus)

  # Sound data
  sound_data = get_sound_data(I2C_bus)

  # Particle data
  # This requires the connection of a particulate sensor (zero/invalid 
  # values will be obtained if this sensor is not present).
  # Specify your sensor model (PPD42 or SDS011) in sensor_functions.py
  # Also note that, due to the low pass filtering used, the 
  # particle data become valid after an initial initialization 
  # period of approximately one minute.
  particle_data = get_particle_data(I2C_bus, PARTICLE_SENSOR)

  with InfluxDBClient(url=InfluxDB_URL, token=token, org=org) as client:
    write_api = client.write_api(write_options=SYNCHRONOUS)
    data = f"env,host={host} temp={air_data['T']:.1f},humidity={air_data['H_pc']:.1f},pressure={air_data['P_Pa']:.0f},"\
    f"aqi={air_quality_data['AQI']:.0f},aqs=\"{interpret_AQI_value(air_quality_data['AQI'])}\",eco2={air_quality_data['CO2e']},"\
    f"voc={air_quality_data['bVOC']},awspl={sound_data['SPL_dBA']},psa={sound_data['peak_amp_mPa']},"\
    f"illum={light_data['illum_lux']},wll={light_data['white']}"
    write_api.write(bucket, org, data)

  #Start Tago logging
  tago_url = "http://api.tago.io/data"
  tago_header = {"Content-type": "application/json","Device-Token":TAGO_DEVICE_TOKEN_STRING}
  try:
      payload = [0]*10;
      payload[0] = {"variable":"temperature","value":f"{air_data['T']:.1f}"}
      payload[1] = {"variable":"pressure","value":f"{air_data['P_Pa']}"}
      payload[2] = {"variable":"humidity","value":f"{air_data['H_pc']:.1f}"}
      payload[3] = {"variable":"aqi","value":f"{air_quality_data['AQI']:.1f}"}
      payload[4] = {"variable":"aqi_string","value":f"{interpret_AQI_value(air_quality_data['AQI'])}"}
      payload[5] = {"variable":"bvoc","value":f"{air_quality_data['bVOC']:.2f}"}
      payload[6] = {"variable":"spl","value":f"{sound_data['SPL_dBA']:.1f}"}
      payload[7] = {"variable":"peak_amp","value":f"{sound_data['peak_amp_mPa']:.2f}"}
      payload[8] = {"variable":"illuminance","value":f"{light_data['illum_lux']:.2f}"}
      requests.post(tago_url, json=payload, headers=tago_header, timeout=2)
      
  except Exception as e:
    # An error has occurred, likely due to a lost internet connection, 
    # and the post has failed.
    # The program will retry with the next data release and will succeed 
    # if the internet reconnects.
    print("HTTP POST failed with the following error:")
    print(repr(e))
    print("The program will continue and retry on the next data output.")
