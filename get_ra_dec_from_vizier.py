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

    parser.add_argument('catName', action='store', choices=['nomad','usnob','2mass','gaia','apass','tycho'], help='The catalogue to search, mandatory')
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
        "apass": "II/336/apass9",       # AAVSO Photometric All Sky Survey (APASS) DR9 (Henden+, 2016)
        "tycho": "I/259/tyc2"       # The Tycho-2 main catalogue (Hog+ 2000)
        }

if args.catName in catalogue_dict :
  vizierCatName = catalogue_dict[args.catName] 
else :
  print ("vizierCatName undefined. Should be impossible. Should have been trapped by argparse above")
  quit()

# Important note on naming table columns.
# There is an open issue on the astroquery github, so it is possible that the behavious may change again at some point.
# What we use here is really just a workaround.
# When astroquery receives column names that contain punctuation or other special characters, it maps them to underscores
# to make them easier to handing in VOTable. That effectively changes the column name though and makes certain
# other astroquery functions not work correctly. The workaround for now is to use column names exactly as they are
# specified in Vizier and ignore the modified names reported in astroquery.
#
# For example
# If you ask astroquery for the column names in Tycho, it replies
# >>> catalogs = Vizier.get_catalogs(Vizier.find_catalogs("I/259/tyc2").keys())
# >>> print(catalogs[0].keys())
# ['TYC1', 'TYC2', 'TYC3', 'pmRA', 'pmDE', 'BTmag', 'VTmag', 'HIP', 'RA_ICRS_', 'DE_ICRS_']
# But if you log into the Vizier website, the coordinates are actually called RA(ICRS), DE(ICRS).
#
# The same happens with filter names in APASS. Astroquery declares the names as i_mag, r_mag, but 
# in Vizier they are i'mag, r'mag.
#
# After all that, the short answer is just specifiy columns as they exist in Vizier itself.
# Check the Vizier web page to get the names, not the astroquery API.


# Each catalogue has different filter names so
# map the generic filter names to specific columns in the Vizier tables
filter_dict = {
        "nomad": {"b":"Bmag",  "v":"Vmag",             "r":"Rmag",              "j":"Jmag", "h":"Hmag", "k":"Kmag" },    # No i in NOMAD
        "usnob": {"b":"B2mag",                         "r":"R2mag", "i":"Imag"                                     },    # Only bri in USNOB
        "2mass": {                                                              "j":"Jmag", "h":"Hmag", "k":"Kmag" },    # Only jhk in 2MASS
        "apass": {"b":"Bmag",  "v":"Vmag",             "r":"r'mag", "i":"i'mag"},
        "gaia":  {"b":"BPmag", "v":"Gmag",             "r":"RPmag"},   # Gaia bands do not map to BVR. Gmag is super broad full optical window.  
        "tycho": {"b":"BTmag", "v":"VTmag"}   # 
        }
if args.filterName in filter_dict[args.catName] :
  vizierFilterName = filter_dict[args.catName][args.filterName]
else :
  print ("Unsupported catalogue and filter combination.")
  quit()


# Each catalogue has different column names for RA DEC
# map the generic RA,DEC to specific columns in the Vizier tables
coord_dict = {
        "nomad": {"RA":"RAJ2000",  "DEC":"DEJ2000"},
        "usnob": {"RA":"RAJ2000",  "DEC":"DEJ2000"},
        "2mass": {"RA":"RAJ2000",  "DEC":"DEJ2000"},
        "apass": {"RA":"RAJ2000",  "DEC":"DEJ2000"},
        "gaia":  {"RA":"RAJ2000",  "DEC":"DEJ2000"},       # Gaia contain both J2000 and ICRS. You can use either.
        "tycho": {"RA":"RA(ICRS)", "DEC":"DE(ICRS)"} 
        }
vizierRA = coord_dict[args.catName]['RA']
vizierDEC = coord_dict[args.catName]['DEC']


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

print(vizierRA, vizierDEC, vizierFilterName)
v = Vizier(catalog=vizierCatName, 
           columns=[vizierRA, vizierDEC, vizierFilterName], 
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

