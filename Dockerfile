FROM python:3

# Metadata
LABEL maintainer="RJS <r.j.smith@ljmu.ac.uk>"
LABEL version="1.0"
LABEL description="Use astroquery python to search various catalogues on Vizier"

#
# Installation dependencies
#

# Can explicitly install packages here in the Dockerfile or can list them in requirements.txt. 
# Generally requirements.txt is tidier and more conventional, but there can be reassons to do it here. 
# See comments below.
WORKDIR /usr/src/app

# Install everything from requirements.txt
RUN pip install --upgrade pip
COPY requirements.txt /usr/src/app/
RUN pip install -r requirements.txt

# Make everything (notably the python script itself) in this directory available to the container.
# Doing this after installing the dependencies means docker can cache the containers efficiently and 
# we do not need to reinstall everything every time we edit the python script.
ADD . /usr/src/app

#
# Open a port using the "EXPOSE" command
# Not using. We are running dockerd with its default TCP port open, specified in the dockerdconfig on the host.
#
# EXPOSE

#
# Following code defines what command to execute when container starts.
#

# Typically people set up Dockers to perform a function as soon as they start
# and then shut down at the end. That is not what I have done with this one.
# I invoke the command I want to run remotely. I.e., I spin up the container
# and specify the command to run in it all at once on the remote client.
# 
# E.g., this gets called from lt-qc with the command:
#
# /usr/bin/docker -H ${dockerURL} run --rm -i $dockerImageName sh -c "python app.py ${centra} ${centdec} ${catRadiusDeg} ${apassFilterName} ${magRange}"
#
# --rm deletes the image when it is closed and not store it.
# -i runs in interactive mode. I.e., dockerd sees this as a person logging in an manually running that "python app.py" command.
# sh -c "COMMAND" executes that COMMAND on the Docker. As described above, this is because I have not defined a CMD or ENTRYPONT in the Dockerfile.

# These are typical examples of CMD, but I am not using it here.
# Run the python script app.py and then close container
#
# Syntax from https://docs.docker.com/engine/reference/builder/
#CMD ["executable","param1","param2"] (exec form, this is the preferred form)
#CMD ["param1","param2"] (as default parameters to ENTRYPOINT)
#CMD command param1 param2 (shell form)
#
# Would using ENTRYPOINT be better?
# Need to read up differences between CMD and ENTRYPOINT

#CMD [ "python", "./app.py", "-v -t" ]
#CMD python app.py 20 20 10 i_mag
# Run a python shell
#CMD [ "python" ]
#
# Run a command line shell
#CMD [ "sh" ]



#--------------------------------------------------
# Usage examples

# sudo docker build -t astroquery .
# Build the Dockerfile in $PWD

# sudo docker run -d astroquery
# Runs 'detached' so you will not see the output

# In order to start dockerd with the tcp port open...
#
# sudo systemctl edit docker
# And put the following in the service file
# [Service]
# ExecStart=
# ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375

