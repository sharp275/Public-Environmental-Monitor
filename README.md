# Public-Environmental-Monitor



In this project, I utilized the Metriful MS430 sensor board and a Raspberry Pi 4b to monitor various indoor environmental variables.  
The data is upload to both a time series database in [InfluxDB Cloud](https://www.influxdata.com/products/influxdb-cloud/) and to [Tago.IO](https://tago.io/), a cloud based solution for IoT.  Both of these have free tiers.
<figure align="center">
<img src="MS430.png"/>
<figcaption align = "center"><b>© 2020 Metriful Ltd.</b></figcaption>
</figure>


The [log_data_to_InfluxDB.py](log_data_to_InfluxDB.py) is a modification of the IoT cloud logging files supplied by Metriful Ltd.  

The SDS011 particle sensor only has a lifetime about one year under continous operation and is costly for a personal project.  
Therefore, it is desrable to only have it run periodically.  The method given by Mertiful requires additional electronics I don't have easy access to obtain.  
The SDS011 does ship with a serial USB interface and this can utilized to not only abtain data but also set a working period.  
This means I needed to write a new Python script to obtain data from the SDS011 and send the data to InfluxDB Cloud and Tago.IO.  
The file for doing this is [Particle_Logging.py](Particle_Logging.py) and requires the SDS011 python package installed.  



[Tago.IO](https://admin.tago.io/public/dashboard/5f0b358bbbca64001c768d0d/fed9d914-bb09-43f3-a171-f38501f29d74)\
[Grafana Cloud](https://sharp275.grafana.net/dashboard/snapshot/Q1mVUopp8ebjwyqZFnxlJmAXDIBwBSgj?orgId=1&refresh=5m)