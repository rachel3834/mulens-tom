######################################################################################################
#                            UTILITY FUNCTIONS
#
# Basic useful utility functions
######################################################################################################

#########################
# PACKAGE IMPORT
from HTMLParser import HTMLParser
import urllib2
import sys
from cStringIO import StringIO
from urllib import urlencode
import cookielib
import ssl
import numpy as np
import hashlib
from os import path, remove
from datetime import datetime
from astropy.time import Time
from pyslalib import slalib as S
from astropy import constants

##################################
# CONVERT SHORT TO LONG EVENT NAME
def short_to_long_name(short_name):
    '''Function to convert the name of a microlensing event in short-hand format to long-hand format.
    Input: Microlensing name string in short-hand format, e.g. OB150001
    Output: Long-hand name format, e.g. OGLE-2015-BLG-0001
           If an incompatible or long-hand name string is given, the same string is returned.
    '''

    # Definitions:
    survey_codes = { 'OB': 'OGLE', 'KB': 'MOA' }

    # Split the string into its components:
    survey = short_name[0:2]
    year = short_name[2:4]
    number = short_name[4:]

    # Interpret each component of the name string:
    if survey in survey_codes.keys():
        survey = survey_codes[survey]
        year = '20' + year
        while len(number) < 4: number = '0' + number

        long_name = survey + '-' + year + '-BLG-' + number
    else:
        long_name = short_name

    return long_name

##################################
# CONVERT LONG TO SHORT EVENT NAME
def long_to_short_name(long_name):
    '''Function to convert the name of a microlensing event in long-hand format to short-hand format.
        Input: Microlensing name string in long-hand format, e.g. OGLE-2015-BLG-0001
        Output: Long-hand name format, e.g. OB150001
        If an incompatible or long-hand name string is given, the same string is returned.
        '''
    
    # Definitions:
    survey_codes = { 'OGLE': 'OB', 'MOA': 'KB' }

    # Split the string into its components:
    components = long_name.split('-')

    # Interpret each component of the name string:
    if len(components) == 4:
        survey = components[0]
        if survey in survey_codes.keys():
            survey = survey_codes[survey]
            year = components[1][2:]
            number = components[3]
            while len(number) < 4: number = '0' + number
        
            short_name = survey + year + number
        else:
            short_name = long_name
    else:
        short_name = long_name

    return short_name

###################################
# FETCH AND PARSE A URL PAGE
def get_http_page(URL, parse=True):
    '''Function to query the parsed URL which is secured with a user ID and
        password.  Return the text content of the page with the HTML tags removed.
        Also handles common HTML errors.'''
    
    # Initialise:
    page_text = ''
    msg = ''
    dbg = True
    
    try:
        response = urllib2.urlopen(URL,context=ssl._create_unverified_context())
        page_data = response.read()
        #print 'Page',page_data
        if parse == True:    
            parser = HTML2Text()
            parser.feed(page_data)
            page_text = parser.get_text()
        else:
            page_text = page_data
    except urllib2.HTTPError:
        msg = 'Error opening webpage'

    return page_text, msg

#####################################
# FETCH SECURE URL
def get_secure_url(URL,login):
    '''Function to fetch the page data from a secured URL.  Login is a tuple containing the 
        user ID and password required, or None.'''
    
    # Build and encode authentication details, establish a cookie jar:
    values = { 'userid' : login[0], 'password': login[1] }
    data = urlencode(values)
    cookies = cookielib.CookieJar()

    # Build a page opener:
    opener = urllib2.build_opener(urllib2.HTTPRedirectHandler(),
                          urllib2.HTTPHandler(debuglevel=0),
                          urllib2.HTTPSHandler(debuglevel=0),
                          urllib2.HTTPCookieProcessor(cookies))

    # Fetch and parse the page data:
    try:
        response = opener.open(URL,data)
        PageText = response.read()
        parser = HTML2Text()
        parser.feed(PageText)
        page_text = parser.get_text()
    except urllib2.HTTPError:
        page_text = urllib2.HTTPError

    return page_text

#############################
# HTML to text converter class
class HTML2Text(HTMLParser):
    """
        extract text from HTML code
        """
    def __init__(self):
        HTMLParser.__init__(self)
        self.output = StringIO()
    def get_text(self):
        """get the text output"""
        return self.output.getvalue()
    def handle_starttag(self, tag, attrs):
        """handle <br> tags"""
        if tag == 'br':
            # Need to put a new line in
            self.output.write('\n')
    def handle_data(self, data):
        """normal text"""
        self.output.write(data)
    def handle_endtag(self, tag):
        if tag == 'p':
            # end of paragraph. Add newline.
            self.output.write('\n')


###################################
# COORDINATE STRING CONVERSION

def sex2decdeg(ra_str,dec_str):
    '''Function to convert an RA and Dec in sexigesimal format to decimal degrees'''
    
    ra_hrs = sexig2dec(ra_str)
    ra_deg = ra_hrs * 15.0
    dec_deg = sexig2dec(dec_str)
    
    return (ra_deg, dec_deg)

def decdeg2sex(ra_deg,dec_deg):
    """Function to convert RA and Dec in decimal degrees to sexigesimal format"""
    
    ra_str = dec2sexig(ra_deg/15.0)
    dec_str = dec2sexig(dec_deg)
    return ra_str, dec_str
    
def dec2sexig(coord):
    """Function to convert a coordinate in decimal format to sexigesimal format.
    If an RA is given as a float, it is assumed to be in decimal hours."""
    
    if coord < 0:
        sign = '-'
        coord = coord*-1.0
    else:
        sign = ''
    dd = int(coord)
    mm = int((coord - float(dd))*60.0)
    ss = (coord - float(dd) - (float(mm)/60.0))*3600.0
    return sign+str(dd)+':'+str(mm)+':'+str(ss)

def sexig2dec(CoordStr):
    '''Function to convert a sexigesimal coordinate string into a decimal float, returning a value in
        the same units as the string passed to it.'''
    
    # Ensure that the string is separated by ':':
    CoordStr = CoordStr.lstrip().rstrip().replace(' ',':')
    
    # Strip the sign, if any, from the first character, making a note if its negative:
    if CoordStr[0:1] == '-':
        Sign = -1.0
        CoordStr = CoordStr[1:]
    else:
        Sign = 1.0
    
    # Split the CoordStr on the ':':
    CoordList = CoordStr.split(':')
    
    # Assuming this presents us with a 3-item list, the last two items of which will
    # be handled as minutes and seconds:
    try:
        Decimal = float(CoordList[0]) + (float(CoordList[1])/60.0) + (float(CoordList[2])/3600.0)
        Decimal = Sign*Decimal
    except:
        Decimal = 0
    
    # Return with the decimal float:
    return Decimal

def d2r( angle_deg ):
    """Function to convert an angle in degrees to radians"""
    
    angle_rad = ( np.pi * angle_deg ) / 180.0
    return angle_rad

def r2d( angle_rad ):
    """Function to convert an angle in radians to degrees"""
    
    angle_deg = ( 180.0 * angle_rad ) / np.pi
    return angle_deg
    
def separation_two_points(pointA,pointB):
    """Function to calculate the separation between two points on the sky, A and B. 
    Input are tuples of (RA, Dec) for each point in decimal degrees.
    Output is the arclength between them in decimal degrees.
    This function uses the full formula for angular separation, and should be applicable
    at arbitrarily large distances."""
    
    # Convert to radians because numpy requires them:
    pA = ( d2r(pointA[0]), d2r(pointA[1]) )
    pB = ( d2r(pointB[0]), d2r(pointB[1]) )
    
    half_pi = np.pi/2.0
    
    d1 = half_pi - pA[1]
    d2 = half_pi - pB[1]
    dra = pA[0] - pB[0]
    
    cos_gamma = ( np.cos(d1) * np.cos(d2) ) + \
                        ( np.sin(d1) * np.sin(d2) * np.cos(dra) )
    gamma = np.arccos(cos_gamma)
    
    gamma = r2d( gamma )
    
    return gamma
    
####################################
# TIME UTILITIES
def ts_to_hjd(ts, target_position, debug=False):
    """Convert a UTC timestamp in YYYY-MM-DDTHH:MM:SS string format to HJD, 
    for a given target position"""
    
    ra_rads = d2r( target_position[0] )
    dec_rads = d2r( target_position[1] )
    target_position = S.sla_dcs2c( ra_rads, dec_rads )
    t = Time(ts, format='isot', scale='utc')
    hjd = jd_to_hjd(t, target_position, debug=debug)
    
    return hjd
    
def jd_to_hjd(t, target_position, debug=False):
    """Calculate the HJD timestamp corresponding to the JD given for the
    current event. 
    Inputs:
        t is an astropy Time object
        target_position is a tuple of (RA, Dec) in decimal degrees
    Outputs:
        hjd  float
    """
    
    if debug == True:
        print 'TIME JD: ',t, t.jd
        
    # Calculate the MJD (UTC) timestamp:
    mjd_utc = t.jd - 2400000.5
    if debug == True:
        print 'TIME MJD_UTC: ',mjd_utc
    
    # Correct the MJD to TT:
    mjd_tt = mjd_utc2mjd_tt(mjd_utc)
    if debug == True:
        print 'TIME MJD_TT: ',mjd_tt, t.tt.jd
    
    # Calculate Earth's position and velocity, both heliocentric
    # and barycentric for this date
    (earth_helio_position, vh, pb, vb) = S.sla_epv( mjd_tt )
    if debug == True:
        print 'Earth Cartesian position: ',earth_helio_position
        print 'Target cartesian position: ', target_position
    
    # Calculate the light travel time delay from the target to 
    # the Sun:
    dv = S.sla_dvdv( earth_helio_position, target_position )            
    tcorr = dv * ( constants.au.value / constants.c.value )
    
    if debug == True:
        print 'TIME tcorr: ', tcorr, 's', (tcorr/60.0),'mins'
    
    # Calculating the HJD:
    hjd = mjd_tt + tcorr/86400.0 + 2400000.5
    if debug == True:
        print 'TIME HJD: ',hjd,'\n'

    return hjd
    
def mjd_utc2mjd_tt(mjd_utc, dbg=False):
    '''Converts a MJD in UTC (MJD_UTC) to a MJD in TT (Terrestial Time) which is
    needed for any position/ephemeris-based calculations.
    UTC->TT consists of: UTC->TAI = 10s offset + 24 leapseconds (last one 2009 Jan 1.)
    	    	    	 TAI->TT  = 32.184s fixed offset'''
# UTC->TT offset
    tt_utc = S.sla_dtt(mjd_utc)
    if dbg: print 'TT-UTC(s)=', tt_utc

# Correct MJD to MJD(TT)
    mjd_tt = mjd_utc + (tt_utc/86400.0)
    if dbg: print 'MJD(TT)  =  ', mjd_tt

    return mjd_tt

#####################################
# MD5SUM
def md5sum( file_path ):
    """Function to calculate the MD5 checksum of a given file"""

    def hash_file( file_path, hasher, blocksize=65536 ):
        fileobj = open(file_path, 'rb')
        buf = fileobj.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fileobj.read(blocksize)
        return hasher.hexdigest()
        
    check_sum = hash_file( file_path, hashlib.md5() )
    return check_sum
