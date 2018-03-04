__author__ = "JC"
__credits__ = ["JC"]
__license__ = "GPL"
__version__ = "1.0"

#models.py
Source code for creating the Catalog Database

#catalogSampleData.py
Code to insert records into the Catalog db in order to have some sample data to view.

#catalogView.py
Server Source code.

#client_secret.json
google app dev credentials for login in with google as third party.

Assumptions
- you have vagrant installed in your machine

Setup:

1. download catalog.zip file.
2. unzip catalog.zip file into your vagrant directory.
3. Open Git Bash
4. go to your vagrant directory
5. execute vagrant up.
6. execute vagrant ssh
7. cd into /vagrant/catalog
8. execute python models.py (to create the Catalog DB)
9. execute catalogSampleData.py (to add sample data)
10. execute catalogView.py
11. Open Browser and enter: http://localhost:5000/catalog
12. Take a look around.

