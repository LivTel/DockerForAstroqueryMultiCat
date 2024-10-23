from timeit import default_timer as timer
preImports = timer()

import os, sys, argparse
#import numpy as np
#from astropy.io import fits

import astropy.units as u
from astropy.coordinates import SkyCoord
from astroquery.vizier import Vizier

#import inspect

# The syntax, list and order of searchable parameters is defined by what it was on
# RMB's APASS REST webservice. I have not defined anything new, just used his specification for compatibility.
# It is not super user friendly or intuitive because it was designed as a REST API, not a human interface.

preArgparse = timer()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run search on Vizier')

    parser.add_argument('catName', action='store', choices=['nomad','usnob','2mass','gaia','apass'], help='The catalogue to search, mandatory')
    parser.add_argument('centra', action='store', type=float, help='Target RA, degrees, mandatory')
    parser.add_argument('centdec', action='store', type=float, help='Target dec, degrees, mandatory')
    parser.add_argument('radius', action='store', type=float, help='Search radius, degrees, mandatory')
    parser.add_argument('filterName', action='store', choices=['b','v','g','r','i','j','h','k'], help='Filter name, mandatory')
    parser.add_argument('magRange', action='store', help='Range in Vizier range syntax: brightLim..faintLim, mandatory')

    #parser.add_argument('-d', dest='displayImage', action='store_true', help='Display the result as well as save FITS (default: Off)')
    parser.add_argument('-v', dest='verbose', action='store_true', help='Turn on verbose mode (default: Off)')
    parser.add_argument('-t', dest='timing', action='store_true', help='Turn on timing reports (default: Off)')
    # -h is always added automatically by argparse1

    args = parser.parse_args()


# Map friendly catalogue names to the Vizier ID codes
catalogue_dict = {
        "nomad": "I/297",        # NOMAD Catalog (Zacharias+ 2005)
        "usnob": "I/284",        # The USNO-B1.0 Catalog (Monet+ 2003) data (around 0+0)
        "2mass": "II/246",       # 2MASS All-Sky Catalog of Point Sources (Cutri+ 2003)
        "gaia": "I/355/gaiadr3",         # Gaia DR3 Part 1. Main source (Gaia Collaboration, 2022)
        "apass": "II/336/apass9"        # AAVSO Photometric All Sky Survey (APASS) DR9 (Henden+, 2016)
        }

if args.catName in catalogue_dict :
  vizierCatName = catalogue_dict[args.catName] 
else :
  print ("vizierCatName undefined. Should be impossible. Should have been trapped by argparse above")
  quit()


# Each catalogue has different filter names so
# map the generic filter names to specific columns in the Vizier tables
filter_dict = {
        "nomad": {"b":"Bmag", "v":"Vmag",             "r":"Rmag",              "j":"Jmag", "h":"Hmag", "k":"Kmag" },    # No i in NOMAD
        "usnob": {"b":"B2mag",                        "r":"R2mag", "i":"Imag"                                     },    # Only bri in USNOB
        "2mass": {                                                             "j":"Jmag", "h":"Hmag", "k":"Kmag" },    # Only jhk in 2MASS
        "apass": {"b":"Bmag", "v":"Vmag",             "r":"r_mag", "i":"i_mag"},
        "gaia":  {"v":"Gmag", "b":"BPmag", "r":"RPmag"}   # Gaia bands do not map to BVR. Gmag is super broad full optical window.  
        }

if args.filterName in filter_dict[args.catName] :
  vizierFilterName = filter_dict[args.catName][args.filterName]
else :
  print ("Unsupported catalogue and filter combination.")
  quit()


if args.verbose:
  print("COMMAND LINE OPTIONS")
  print (args)
  print("\nCATALOGUE")
  print ("Catalogue name re-mapped for Vizier to", vizierCatName)
  catlist = Vizier.find_catalogs(vizierCatName)
  for k, v in catlist.items():
      print(k, ":", v.description)
  catalogs = Vizier.get_catalogs(Vizier.find_catalogs(vizierCatName).keys())
  print(catalogs)
  print(catalogs[0][1])
  print("List of available keys in this catalogue:")
  print(catalogs[0].keys())
  print("\nFILTER")
  print ("Filter name re-mapped for Vizier to", vizierFilterName)
  print("\n")
  
preQuerySetup = timer()

cent = SkyCoord(ra=args.centra*u.degree, dec=args.centdec*u.degree, frame='fk5')

v = Vizier(catalog=vizierCatName, 
           columns=["RAJ2000","DEJ2000",vizierFilterName], 
           column_filters={vizierFilterName:args.magRange},
           row_limit=10000)

#for name, value in inspect.getmembers(v):
#  if not name.startswith('_'):
#    print(f"{name}: {value}")

preQuery = timer()
result = v.query_region(cent, radius=args.radius*u.degree)

preDisplay = timer()

if len(result) :
  result[0].pprint_all(show_name=args.verbose, show_unit=args.verbose, show_dtype=False)
else :
  if args.verbose :
    print("No search results")
  

if args.timing:
  print("Imports duration = ",preArgparse-preImports,"sec")
  print("Argparse duration = ",preQuerySetup-preArgparse,"sec")
  print("QuerySetup duration = ",preQuery-preQuerySetup,"sec")
  print("Query duration = ",preDisplay-preQuery,"sec")
  print("Display duration = ",timer()-preDisplay,"sec")

