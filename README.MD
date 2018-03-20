
__author__ = "JC, Udacity" 
__credits__ = ["JC, Udacity"] 
__license__ = "GPL" 
__version__ = "1.0" 

IP address: 18.188.97.153 

Catalog app URL: http://18.188.97.153.xip.io/catalog/ 

Software installed: 
- Finger 
- Apache2 
- libapache2-mod-wsgi 
- postgregsql 
- python-pip 
- python-psycopg2 
- git 

Configurations made: 
- Update all currently installed packages. 
- Change the SSH port from 22 to 2200 
- Configured UFW to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123) 
- created new user: grader, with permission to sudo 
- created and configured SSH key pair for grader and ubuntu user using ssh-keygen tool. 
- configured the local timezone to UTC 
- created db user catalog in postgresql 

Third-Party resource: - N/A
