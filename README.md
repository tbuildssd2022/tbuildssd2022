# ISS Secure File Repository Installation #############

The Secure File Repository (SFR) application can be implemented as a distributed service, requiring at least one Flask web application framework, hereafter referred to as an “MVC node”, and a MySQL database, hereafter referred to as a “data tier”. Both components can reside on a single server or separate devices with network connectivity permitting inbound TCP connections from the MVC node to the data tier, typically port 3306. The Flask framework webserver is not recommended for internet facing or production scenarios, protection solutions such as an HTTP proxy are beyond the scope of this readme. 


## Software installation
Within the GitHub repository there are two main directories, server_build contains utilities configuration files needed for the initial implementation of the solution. These utilities include the standalone python CLI application providing user registration functions as well as an SQL script for creating the application database and a sample dataset which can be restored to the database once created. The “app” directory is the home location of the application and can be located anywhere on the MVC node that is readable by the user running the application. 

1.	Git clone https://github.com/tbuildssd2022/tbuildssd2022.git

## MVC infrastructure preparation
The Flask server operating system is presumed to be Linux with the following core packages installed and all package dependencies automatically included:
python3, python3-pip

1.	Create a non-privileged user on the MVC node 
2.	Recursively copy the contents of the SFR app directory to the non-privileged user’s home directory E.G.  cp -R ./app /opt/appuser
3.	Change user context to the non-privileged user, E.G., sudo su - appuser
4.	While in the appuser context, install the required python packages using the library file requirements.txt with the following command:

pip3 install --user -r requirements.txt

5.	Add flask to the appuser’s path with the following command:
export PATH=$PATH:/opt/appuser/.local/bin
6.	Modify the database connection settings within the env-dev file and save as.env in the app/sfrapp directory 


## Data tier infrastructure preparation
The data tier can be any operating system or container supporting MySql version 8.
1.	Modify the user password and IP restrictions in the file sfrdev-v3.sql, located in the server_build directory to suit the local network.
2.	Create an application database using the sfrdev-v3.sql file with the following command:

mysql -u root -p sfrdev < /path/to/sfrdev-v3.sql

3.	Restore the sample database content using the following command:
mysql -u root -p sfrdev < /path/to/sdrdev_dump.sql

4.	Alternatively use the file mksfruserdev.py to create new users for the application.


## Starting the SFR application

1. Change directory to the application home folder, download-location/tbuildssd2022/app
2. Export two environment variables as shown below (use development if verbose console output needed):

    export FLASK_APP=sfrapp
    export FLASK_ENV=production

3. Start the flask server, specifying the IP address and TCP port to listen on as shown below:
    flask run -h 10.100.200.6. -p 8080




