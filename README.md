Face Similarity API
==========================
Process image to obtain 128 vector dimensions and calculate distance.
The distance represents the similarity between both faces.

System requirements
-------------------
- Python >= 3.6

Installation
------------
```bash
$ sudo mkdir /var/log/fksolutions  # creates fksolutions logging folder
$ sudo chown $USER:$USER /var/log/fksolutions  # give fksolutions logging folder group permissions
$ pip install -e .
```

Usage
-----
```bash
$ face-similarity  # run API
```
Read REST API documentation through ``/docs`` endpoint for API usage.