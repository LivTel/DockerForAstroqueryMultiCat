# DockerForAstroqueryMultiCat
Very simple python script designe to emulate RMB's APASS web service by wrapping astropy astroquery searches on Vizier. It is used to provide astrometric catalogues to wcs_fit on lt-qc and photometric catalogues to the skycam photometricity monitor. The Docker image sits on one of th ltvmhosts, contains a python script and can be called from any other ARI LAN machine.

The Dockerfile is incredibly simplistic since this is a really minimal python script.  The Dockerfile calls the default 'python3' image and installs the couple of python packages listed the in requiremnets.txt. I do not need to mount any disks or construct any bespoke runtime environment for the simple script work. The sprat pipeline Docker (https://github.com/LivTel/sprat_l2_pipeline/tree/dockerised_binning) demonstrates many more features than this.

# Instructions

``git clone https://github.com/LivTel/DockerForAstroqueryMultiCat.git``

``cd DockerForAstroqueryMultiCat``

``sudo docker build -t astroquery .``

This was developed on ltvmhost1. If you have spun this up on a different vmhost, you probably also want to update the target URL in any scripts that make use of this service. For example the
lt-qc:/usr/local/bin/wcs_fit script contains
``set dockerURL = "tcp://150.204.240.151:2375"``

# Network Ports

In order to start dockerd on the host with a tcp port open so it can be addressed from a remote host

``sudo systemctl edit docker``
 
And put the following in the service file

> [Service]<br>
> ExecStart=<br>
> ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375

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

``set dockerURL = "tcp://150.204.240.151:2375"``

``set dockerImageName = astroquery``

``/usr/bin/docker -H ${dockerURL} run --rm -i $dockerImageName python get_ra_dec_from_vizier.py usnob $RA $DEC $SEARCH_RADIUS r 1..100 >> $RESULT_FILE ``


