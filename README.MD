
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

1. Update all currently installed packages: 
	<br/>a. sudo apt-get update 
	<br/>b. sudo apt-get upgrade 
2. Change the SSH port from 22 to: 
	<br/>a. Use `sudo vim /etc/ssh/sshd_config` and then change Port 22 to Port 2200 , save & quit. 
	<br/>b. Reload SSH using `sudo service ssh restart` 
3. Configured UFW to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123) 
	<br/>a. sudo ufw allow 2200 
	<br/>b. sudo ufw allow 80 
	<br/>c. sudo ufw allow 123 
	<br/>d. sudo ufw enable 
	<br/>e. confirm (sudo ufw status) 
4. Denied access to port 22: 
	<br/>a.sudo ufw deny 22) 
5. created new user: grader, with permission to sudo with prompt for passwrd every time. 
	<br/>a. sudo adduser grader 
	<br/>b. enter password 
	<br/>c. create grader file in /etc/sudoers.d with the following line: "grader ALL=(ALL) ALL" 
	<br/>d. save & quit 
6. created and configured SSH key pair for grader and ubuntu user using ssh-keygen tool. 
	<br/>a. run ssh-keygen in my local machine (not the aws server) 
	<br/>b. give file a name 
	<br/>c. copy public key to the remote server's .ssh/authorized_keys file 
7. configured the local timezone to UTC 
	<br/>a. sudo dpkg-reconfigure tzdata (follow prompt) 
8. created db user catalog in postgresql 
	<br/>a. sudo -u postgres createuser catalog 
	<br/>b. grant all privileges on database catalogDB to catalog ; 
9. configured automatic updates using the unattended-upgrades package
	<br/>a. enabled it using the following command: "sudo dpkg-reconfigure --priority=low unattended-upgrades" 

Third-Party resource: 

- N/A
