# DockerForAstroqueryMultiCat
Very simple python script designe to emulate RMB's APASS web service by wrapping astropy astroquery searches on Vizier. It is used to provide astrometric catalogues to wcs_fit on lt-qc and photometric catalogues to the skycam photometricity monitor. The Docker image sits on one of th ltvmhosts, contains a python script and can be called from any other ARI LAN machine.

The Dockerfile is incredibly simplistic since this is a really minimal python script.  The Dockerfile calls the default 'python3' image and installs the couple of python packages listed the in requirements.txt. I do not need to mount any disks or construct any bespoke runtime environment for the simple script work. The sprat pipeline Docker (https://github.com/LivTel/sprat_l2_pipeline/tree/dockerised_binning) demonstrates many more features than this.

# Instructions

``git clone https://github.com/LivTel/DockerForAstroqueryMultiCat.git``

``cd DockerForAstroqueryMultiCat``

``sudo docker build -t astroquery .``

This was developed on ltvmhost1. If you have spun this up on a different vmhost, you probably also want to update the target URL in any scripts that make use of this service. For example the
lt-qc:/usr/local/bin/wcs_fit script contains
``set dockerURL = "tcp://150.204.240.151:2375"``

# Network Ports

## Unsecured

In order to start dockerd on the host with an **unsecured tcp port open** so it can be addressed from any remote host without authentication

``sudo systemctl edit docker``
 
And put the following in the service file

> [Service]<br>
> ExecStart=<br>
> ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375

``sudo systemctl restart docker``

## Secured

In order to start dockerd on the host with a **TLS secured tcp port open** so it can be addressed from any remote host using TLS certificates
is obviously _far_ more complicated.

On the vmhost, we will create the TLS certificates in ~eng/docker_ssl. You will need to provide a _secret_ which will need to be stored in
our secrets and passwords records, though obvously not mentioned here.

In this example I am running on ltvmhost5, 150.204.240.157, but if oyu run on a different vmhost you will need to set the name and IP.

<pre><code>
cd /home/eng
sudo su
mkdir docker_ssl
cd docker_ssl
openssl genrsa -aes256 -out ca-key.pem 4096
openssl req -new -x509 -days 36500 -key ca-key.pem -sha256 -out ca.pem
openssl genrsa -out server-key.pem 4096
openssl req -subj "/CN=ltvmhost5" -sha256 -new -key server-key.pem -out server.csr
echo subjectAltName = DNS:ltvmhost5,IP:150.204.240.157 >> extfile.cnf
echo extendedKeyUsage = serverAuth >> extfile.cnf
openssl x509 -req -days 36500 -sha256 -in server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -extfile extfile.cnf
</code></pre>

Next create the certificates for the client

<pre><code>
openssl genrsa -out key.pem 4096
openssl req -subj '/CN=client' -new -key key.pem -out client.csr
echo extendedKeyUsage = clientAuth > extfile-client.cnf
openssl x509 -req -days 36500 -sha256 -in client.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out cert.pem -extfile extfile-client.cnf
chmod 666 ca.pem cert.pem key.pem
</code></pre>

Copy ca.pem cert.pem key.pem to the client that is going to want to access this dockerd

``sudo systemctl edit docker``

And put the following in the service file

> [Service]
> ExecStart=
> ExecStart=/usr/bin/dockerd --tlsverify --tlscacert=/home/eng/docker_ssl/ca.pem --tlscert=/home/eng/docker_ssl/server-cert.pem --tlskey=/home/eng/docker_ssl/server-key.pem -H fd:// -H=tcp://0.0.0.0:2376

``sudo systemctl restart docker``


# Runtime syntax

The syntax, list and order of searchable parameters is defined by what it was on RMB's APASS REST webservice. I have not defined anything new, just used his specification for compatibility. It is not super user friendly or intuitive because it was designed as a REST API, not a human interface. The input parameters are an ordered list, all are mandatory and the order important. It is probably not a tool you want to use frequently interactively. You would be better off just using astroquery itself directly.

``python get_ra_dec_from_vizier.py  CATALOG RA DEC RADIUS FILTER MAGNITUDE_RANGE``

* CATALOG = ['nomad','usnob','2mass','gaia','apass']
* RA = Search position in degrees
* DEC = Search position in degrees
* RADIUS = Circular search radius in degrees
* FILTER = ['b','v','g','r','i','j','h','k']
* MAGNITUDE_RANGE = search limits in the Vizier range syntax ("min..max"). So 10 < r < 20 would be written "r 10..20"

Optional "-v" creates verbose output to STDOUT. Otherwise the only return is a three column list of RA DEC, MAG.


# Usage examples



Run it 'detached' with -d to be able to see the output

``sudo docker run -d astroquery``

To start the docker in 'interactive mode' so you can log into it and run jobs manually.

``sudo docker run -it astroquery``

In normal ops it is notleft running continuously. It only takes a faction of a second to invokde it from the stored image
so it is launched on demand to run a search and then closes down.

Following is an example extracted from wcs_fit. This searches USNOB with effectively no magnitude cut, 1 < R2mag < 100. This should run from anywhere in the ARI LAN.


And then one of the following, depending whather you are using TLS security or not.

``set dockerImageName = astroquery``
``set dockerURL = "tcp://150.204.240.151:2375"``
``/usr/bin/docker -H ${dockerURL} run --rm -i $dockerImageName python get_ra_dec_from_vizier.py usnob $RA $DEC $SEARCH_RADIUS r 1..100 >> $RESULT_FILE ``

``set dockerImageName = astroquery``
``set dockerURL = "tcp://150.204.240.157:2376"``
``/usr/bin/docker --tlsverify --tlscacert=ca.pem --tlscert=cert.pem --tlskey=key.pem -H ${dockerURL} run --rm -i $dockerImageName python get_ra_dec_from_vizier.py usnob $RA $DEC $SEARCH_RADIUS r 1..100 >> $RESULT_FILE ``


