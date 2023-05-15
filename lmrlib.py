#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 15 15:57:55 2023

@author: sbiri
"""
import numpy as np


# based on fortran code in https://icoads.noaa.gov/software/lmrlib
#=============================================================================#
# Comprehensive Ocean-Atmosphere Data Set (COADS):   Fortran 77 Program+Shell #
# Filename:level: lmrlib:01G                                 17 November 2004 #
# Function: Tools to assist conversions into LMR6   Author: S.Woodruff et al. #
#=============================================================================#
# Software Revision Information (previous version: 17 Aug 2000, level 01F):
# Remove print statements and remaining stop from {ixdtnd,rxnddt}.
#-----------------------------------------------------------------------3456789
# Software documentation for the (modifiable) library test routine {libtst},
# and for the remaining (invariant) user-interface routines in the library.
#
# Functionality:  This is a library of tools to assist conversions from other
# formats into LMR6, whose functions are individually described in the comments
# at the beginning of each subroutine or function.  The following naming and
# other conventions have been applied:
#     1) Subprogram (function or subroutine) names begin with a letter
#     indicating their type or function:
#          a) "f" for type real (floating point)
#          b) "i" for type integer
#          #) "r" for subroutines
#          d) "t" for test and other software development subroutines.
#     2) The second letter of subprogram names indicates:
#          a) "x" for subprograms for units and related conversions.  Units
#          "to" and "from" generally compose the remainder of the name as
#          2-letter abbreviations in that order (e.g., ixbfkt is an integer
#          function that maps Beaufort numbers into speed midpoints in kts).
#          b) "w" for subprograms for corrections.  Presently these are
#          limited to barometric corrections, with "bp" in letters 3-4.
#          c) "p" for subprograms producing only printed results.
#          d) "m" for miscellaneous subprograms.
#     3) Each subprogram includes specific declarations of the type of each
#     input and output argument (implicit and default typings are not used
#     for external communication; they may be used internally to subprograms).
#     4) Input/output arguments (or function returns) that are most naturally
#     represented as integers, are typed as such.  Users will need to make
#     transformations from/to real variables, as needed.
#     5) Errors detected within the library generally result in a printed
#     statement including the name of the library routine involved, and then
#     a stop.  Exceptions are {ixdtnd,rxnddt}, which return -1 instead of stopping,
#     and {ix32dd,ixdcdd}, which return a user-supplied missing value.
#     6) Portions of the library can be exhaustively tested by running the
#     library test routine {libtst}, which should yield no output (unless
#     errors are printed).  
# Contents:  Following are the routines included, and their broader groupings:
#      barometric conversions:
#           {fxmmmb}     millimeters Hg to millibars
#           {fxmbmm}     millibars to millimeters Hg
#           {fxeimb}     inches (English) Hg to millibars
#           {fxmbei}     millibars to inches (English) Hg
#           {fxfimb}     inches (French) Hg to millibars
#           {fxmbfi}     millibars to inches (French) Hg, plus
#                        entry points {fxfim0,fxfim1} used by {tpbpfi}
#           {fwbptf}     correction value for temperature (Fahrenheit)
#           {fwbptc}     correction value for temperature (Celsius)
#           {fwbptg}     correction value for temperature (generalized)
#           {fwbpgv}     correction value for gravity
#      cloud conversions:
#           {ixt0ok}     tenths (of sky clear  ) to oktas (of sky covered)
#           {ixt1ok}     tenths (of sky covered) to oktas (of sky covered)
#      temperature conversions:
#           {fxtftc}     Fahrenheit to Celsius
#           {fxtctf}     Celsius to Fahrenheit
#           {fxtktc}     Kelvins to Celsius
#           {fxtctk}     Celsius to Kelvins
#           {fxtrtc}     Reaumur to Celsius
#           {fxtctr}     Celsius to Reaumur
#      wind conversions:
#           {fxuvdd}     vector (u,v) components to direction (degrees)
#           {fxuvvv}     vector (u,v) components to velocity
#           {rxdvuv}     direction and speed to vector (u,v) components
#           {fxktms}     knots to m/s (ref. international nautical mile)
#           {fxmskt}     m/s to knots (ref. international nautical mile)
#           {fxk0ms}     knots to m/s (ref. US nautical mile)
#           {fxmsk0}     m/s to knots (ref. US nautical mile)
#           {fxk1ms}     knots to m/s (ref. Admiralty nautical mile)
#           {fxmsk1}     m/s to knots (ref. Admiralty nautical mile)
#           {ixbfkt}     0-12 Beaufort number to knots (WMO code 1100)
#           {fxbfms}     0-12 Beaufort number to m/s (WMO code 1100)
#           {ix32dd}     32-point direction abbreviation into code and degrees
#           {ixdcdd}     32-point direction code into degrees
#      time conversions:
#           {rxltut}     local standard hour and "Julian" day into UTC
#           {ixdtnd}     date to days ("Julian") since 1 Jan 1770
#           {rxnddt}     days ("Julian") since 1 Jan 1770 to date
#      miscellaneous:
#           {rpepsi}     print machine epsilon
#           {rpepsd}     double precision version of {rpepsi}
#           {imrnde}     round to nearest even integer
# Machine dependencies:  None known.
# For more information: See <soft_info> and <soft_lmr> (electronic documents).
#-----------------------------------------------------------------------
#=======================================================================
#-----barometric conversions--------------------------------------------
#=======================================================================
def fxmmmb(mm):
    """
    Converts barometric pressure in (standard) millimeters of mercury (mm)
    to millibars (hPa), e.g., fxmmmb(760.) = 1013.25 (one atmosphere)
    (List, 1966, p. 13).
    sdw, 23 Nov 1999.
    sdw, 25 Feb 2000: changes to comments.
    References:
    List, R.J., 1966: Smithsonian Meteorological Tables.
        Smithsonian Institution, Washington, DC, 527 pp.
    WMO (World Meteorological Organization), 1966: International
        Meteorological Tables, WMO-No.188.TP.94.

    Parameters
    ----------
    mm : float
        barometric pressure in millimeters of mercury (mm)

    Returns
    -------
    fxmmmb : float
        barometric pressure in millibars (hPa)

    """
    #-----factor from List (1966), p. 13 and Table 11; also in WMO (1966).
    fxmmmb = mm*1.333224
    return fxmmmb

#-----------------------------------------------------------------------
def fxmbmm(mb):
    """
    Converts barometric pressure in millibars (hPa; mb) to (standard)
    millimeters of mercury.  Numerical inverse of {fxmmmb} (see for
    background).  Note: This method yields better numerical agreement 
    in cross-testing against that routine than the factor 0.750062.
    sdw, 26 Jan 2000.
    sdw, 25 Feb 2000: changes to comments.

    Parameters
    ----------
    mb : float
        barometric pressure in millibars (hPa; mb)

    Returns
    -------
    fxmbmm : float
        barometric pressure in millimeters of mercury (mm)

    """
    fxmbmm = mb/1.333224
    return fxmbmm

#-----------------------------------------------------------------------
def fxeimb(ei):
    """
    Converts barometric pressure in (standard) inches (English) of 
    mercury (in) to millibars (hPa), e.g., fxeimb(29.9213) = 1013.25 
    (one atmosphere) (List, 1966, p. 13).
    sdw, 26 Jan 2000.
    sdw, 25 Feb 2000: changes to comments.
    References:
    List, R.J., 1966: Smithsonian Meteorological Tables.
    Smithsonian Institution, Washington, DC, 527 pp.
    WMO (World Meteorological Organization), 1966: International 
    Meteorological Tables, WMO-No.188.TP.94.
    ei factor from List (1966), Table 9.  Note: a slightly different factor 
    33.8639 appears also on p. 13 of List (1966), and in WMO (1966).  Tests
    (32-bit Sun f77) over a wide range of pressure values (25.69"-31.73",
    approximately equivalent to ~870-1074.6 mb) indicated that the choice
    of constant made no numeric difference when data were converted to mb
    and then rounded to tenths, except for two cases of 0.1 mb difference
    (25.79" = 873.3/.4 mb; and 26.23" = 888.2/.3 mb).  If 1 mm = 1.333224
    mb and 1" = 25.4 mm, then 25.4mm = 33.86389 to 7 significant digits.

    Parameters
    ----------
    ei : float
        barometric pressure in inches (English) of mercury (in)

    Returns
    -------
    fxeimb : float
        barometric pressure in millibars (hPa)

    """
    fxeimb = ei*33.86389
    return fxeimb
#-----------------------------------------------------------------------
def fxmbei(mb):
    """
    Converts barometric pressure in millibars (hPa; mb) to (standard)
    inches (English) of mercury.  Numerical inverse of {fxeimb} (see for
    background).  Note: This method yields better numerical agreement
    in cross-testing against that routine than the factor 0.0295300.
    sdw, 26 Jan 2000.

    Parameters
    ----------
    mb : float
        barometric pressure in millibars (hPa; mb)

    Returns
    -------
    fxmbei : float
        barometric pressure in inches of mercury (in)

    """
    fxmbei = mb/33.86389
    return fxmbei

#-----------------------------------------------------------------------
def fxfimb(fi):
    """
    Converts barometric pressure in inches (French) of mercury (fi) to
    millibars (hPa).  Paris, instead of French, inches are referred
    to in Lamb (1986), but these appear to be equivalent units.  Note:
    data in lines (twelve lines per inch) or in inches and lines need
    to be converted to inches (plus any decimal fraction).  Entry points
    {fxfim0,fxfim1}, which are called by {tpbpfi} (see for background)
    are not recommended for use in place of {fxfimb}.
    sdw, 26 Jan 2000.
    References:
    IMC (International Meteorological Committee), 1890: International
    Meteorological Tables, published in Conformity with a Resolution
    of the Congress of Rome, 1879.  Gauthier-Villars et Fils, Paris.
    Lamb, H.H., 1986: Ancient units used by the pioneers of meteorological
    instruments.  Weather, 41, 230-233.

    Parameters
    ----------
    fi : float
        barometric pressure in inches (French) of mercury (fi)

    Returns
    -------
    fxfi : float
        barometric pressure in millibars (hPa)

    """
    # factor for conversion of French inches to mm (IMC, 1890, p. B.2);
    # mm are then converted to mb via {fxmmmb}
    # fxfimb = fxmmmb(fi*27.069953)
    # factor for conversion of French inches to English inches (ibid.); 
    # inches are then converted to mb via {fxeimb}
    # fxfim0 = fxeimb(fi*1.0657653)
    # direct conversion factor to mb from Lamb (1986), Table 1 footnote.
    fxfim1 = fi * 36.1
    return fxfim1
#-----------------------------------------------------------------------
def fxmbfi(mb):
    """
    Converts barometric pressure in millibars (hPa; mb) to inches (French)
    of mercury.  Numerical inverse of {fxfimb} (see for background).
    sdw, 26 Jan 2000.

    Parameters
    ----------
    mb : float
        barometric pressure in millibars (hPa; mb)

    Returns
    -------
    mb : float
        barometric pressure in inches (French) of mercury

    """
    fxmbfi = fxmbmm(mb)/27.069953
    return fxmbfi

#-----------------------------------------------------------------------
def fwbptc(bp, tc):
    """
    Correction value of barometric pressure (in mm or mb; standard
    temperature of scale 0C) (bp) for temperature in Celsius (tc)
    (see {fwbpgt} for additional background).
    sdw, 23 Nov 1999.
    sdw, 25 Feb 2000: changes and additions to comments.
    Reference:
    List, R.J., 1966: Smithsonian Meteorological Tables.
    Smithsonian Institution, Washington, DC, 527 pp.

    Parameters
    ----------
    bp : float
        barometric pressure (in mm or mb; standard temperature of scale 0C)
    tc : float
        temperature in Celsius

    Returns
    -------
    fwbptc : float

    """
    # constants m and l from List (1966), p. 136.
    m, l = 0.0001818, 0.0000184
    fwbptc = -bp*(((m-l)*tc)/(1.+(m*tc)))
    return fwbptc

#-----------------------------------------------------------------------
def fwbptf(bp, tf):
    """
    Correction value of barometric pressure (in inches; standard
    temperature of scale 62F) (bp) for temperature in Fahrenheit (tf)
    (see {fwbpgt} for additional background).
    sdw, 23 Nov 1999.
    sdw, 25 Feb 2000: changes and additions to comments.
    Reference:
    List, R.J., 1966: Smithsonian Meteorological Tables.
    Smithsonian Institution, Washington, DC, 527 pp.

    Parameters
    ----------
    bp : float
        barometric pressure (in inches; standard temperature of scale 62F)
    tf : float
        temperature in Fahrenheit

    Returns
    -------
    fwbptf : float

    """
    # constants m and l from List (1966), p. 137.
    m, l = 0.000101, 0.0000102
    fwbptf = -bp*(((m*(tf-32.))-(l*(tf-62.)))/(1.+m*(tf-32.)))
    return fwbptf

#-----------------------------------------------------------------------
def fwbptg(bp, t, u):
    """
    Correction value (generalized) of barometric pressure (bp) for
    temperature (t), depending on units (u):
                                         standard temperature:
         u  bp          t           of scale (ts)  of mercury (th)
         -  ----------  ----------  -------------  -------------------
         0  mm or mb    Celsius      0        0C
         1  Eng. in.    Fahrenheit  62F (16.667C)  32F (0C) (pre-1955)    
         2  Eng. in.    Fahrenheit  32F (0C)       32F (0C) (1955-)
         3  French in.  Reaumur     13R (16.25C)    0R (0C)
    The returned {fwbptg} value is in the same units as, and is to be
    added to, bp.  Establishment of 0C/32F as the standard temperature
    for both scale and mercury as implemented under u=1 and 3 became
    effective 1 Jan 1955 under WMO International Barometer Conventions
    (WBAN, 12 App.1.4.1--2; see also WMO, 1966 and UKMO, 1969).  List
    (1966), p. 139 states that "the freezing point of water is universally
    adopted as the standard temperature of the mercury, to which all
    readings are to be reduced," but for English units uses only 62F for
    the standard temperature of the scale.  Note: Results under u=4, and
    the utilized settings of constants l and m, have not been verified
    against published values, if available.  IMC (1890, p. B.24) states
    that in "old Russian barometer readings expressed in English half lines
    (0.05 in) the mercury and the scale were set to the same temperature
    62F."  UKMO (1969, p. 5) states that for Met. Office barometers prior
    to 1955 reading in millibars the standard temperature was 285K (12C).
    This routine does not handle these, or likely other historical cases.
    sdw, 23 Nov 1999.
    sdw, 25 Feb 2000: Add u=3-4, plus changes and additions to comments.
    References:
    IMC (International Meteorological Committee), 1890: International
          Meteorological Tables, published in Conformity with a Resolution
          of the Congress of Rome, 1879.  Gauthier-Villars et Fils, Paris.
    List, R.J., 1966: Smithsonian Meteorological Tables.
          Smithsonian Institution, Washington, DC, 527 pp.
    UKMO (UK Met. Office), 1969: Marine Observer's Handbook (9th ed.).
          HMSO, London, 152 pp.
    US Weather Bureau, Air Weather Service, and Naval Weather Service,
          1963: Federal Meteorological Handbook No. 8--Manual of Barometry
          (WBAN), Volume 1 (1st ed.).  US GPO, Washington, DC.
    WMO (World Meteorological Organization), 1966: International
          Meteorological Tables, WMO-No.188.TP.94.

    Parameters
    ----------
    bp : float
        barometric pressure
    t : float
        temperature
    u : int
        units

    Returns
    -------
    None.

    """
    # constants ts and th are from List (1966), pp. 136-137 (u=1-2); WBAN
    # 12 App.1.4.1--3 (u=3); and IMC (1890), p. B.24 (u=4).
    ts, th = [0.0, 62., 32., 13.], [0.0, 32., 32., 0.0]
    # constants m and l are from List (1966), pp. 136-137 (u=1-3) and WBAN,
    # pp. 5-4 and 5-5 (for metric and English units).  For u=4, the u=1
    # constants were multiplied by 5/4 (after List, 1966, p. 137).
    m = [0.0001818, 0.000101, 0.000101, 0.000227]
    l = [0.0000184, 0.0000102, 0.0000102, 0.0000230]
    # test u for valid range
    if u not in range(4):
        print('fwbptg error. invalid u={}'.format(u))
        return
    fwbptg = -bp*(((m[u]*(t-th[u]))-(l[u]*(t-ts[u])))+(1.+(m[u]*(t-th[u]))))
    return fwbptg

#-----------------------------------------------------------------------
def fwbpgv(bp, rlat, gmode):
    """
    Correction value of barometric pressure (bp) for gravity depending on
    latitude (rlat), with constants set depending on gmode (for COADS, we
    adopt gmode=1 for 1955-forward, and gmode=2 for data prior to 1955):
          g1 (equation 1)   g2 (equation 2)   Comment
          ---------------   ---------------   -----------------------------
    0 =          g45               g0         yields List (1966), Table 47B
    1 =          g0                g0         follows GRAVCOR (pre-1955)
    2 =          g45               g45        (of unknown utility)
    The returned {fwbpgv} value is in the same units as, and is to be added
    to, bp (units for bp are unspecified; Table 47B has columns for inches,
    millimeters, and millibars).  Usage of g0 and g45 as implemented under
    gmode=1 became effective 1 Jan 1955 under WMO International Barometer
    Conventions: g45 is a "best" estimate of acceleration of gravity at 45
    deg latitude and sea level, and g0 is the value of standard (normal)
    gravity "to which reported barometric data in mm or inches of mercury
    shall refer, but it does not represent the value of gravity at latitude
    45 deg, at sea level" (WBAN, 12 App.1.4.1--2; see also List, 1966, pp.
    3-4, and WMO, 1966).  For example, UK Met. Office MK I (MK II) barometers
    issued before (starting) 1 January 1955 were graduated to read correctly
    when the value of gravity was g45 (g0) (UKMO, 1969).  As shown by test
    routines {tpbpg1,tpbpg2}, gmode=2 and 3 yield virtually the same results.
    sdw, 4 Dec 1999 (after GRAVCOR, 13 Jan 1999 e-mail fr T. Basnett, UKMO).
    sdw, 2 Feb 2000: changes and additions to comments.
    sdw, 25 Feb 2000: changes and additions to comments.
    References:
    List, R.J., 1966: Smithsonian Meteorological Tables.
          Smithsonian Institution, Washington, DC, 527 pp.
    UKMO (UK Met. Office), 1969: Marine Observer's Handbook (9th ed.).
          HMSO, London, 152 pp.
    US Weather Bureau, Air Weather Service, and Naval Weather Service,
          1963: Federal Meteorological Handbook No. 8--Manual of Barometry
          (WBAN), Volume 1 (1st ed.).  US GPO, Washington, DC.
    WMO (World Meteorological Organization), 1966: International
          Meteorological Tables, WMO-No.188.TP.94.
    

    Parameters
    ----------
    bp : float
        barometric pressure
    rlat : float
        latitude
    gmode : int

    Returns
    -------
    None.

    """
    pi = 3.14159265358979323846264338327950288
    # g45 from List (1966), p. 488 ("best" sea-level gravity at latitude 45)
    g45 = 980.616
    # g0  from List (1966), p. 200 ("standard" acceleration of gravity)
    g0 = 980.665
    # check latitude 
    if (rlat < -90 or rlat>90):
        print('fwbpgv error. invalid rlat={}'.format(rlat))
        return
    # check gmode, and set g1 and g2
    if gmode==0:
        g1 = g45
        g2 = g0
    elif gmode==1:
        g1 = g0
        g2 = g0
    elif gmode==2:
        g1 = g45
        g2 = g45
    else:
        print('fwbpgv error. invalid gmode={}'.format(gmode))
        return
    # convert degrees to radians
    rlatr = rlat*(pi/180.)
    # List (1966), p. 488, equation 1 (c is the local acceleration of gravity)
    a = 0.0000059*(cos(2.0*rlatr)**2)
    b = 1-0.0026373*cos(2.0*rlatr)
    c = g1*(a+b)
    # List (1966), p. 202, equation 2
    fwbpgv = ((c-g2)/g2)*bp
    return fwbpgv

# =======================================================================
# -----cloud conversions-------------------------------------------------
# =======================================================================
def ixt0ok(t0):
    """
    Converts "proportion of sky clear" in tenths (t0), to oktas (eighths
    of sky covered; WMO code 2700).  The t0 code, specified in Maury
    (1854), was documented for use, e.g., for US Marine Meteorological
    Journals (1878-1893).  The dates of transition to instead reporting
    "proportion of sky covered" (t1, as handled by {ixt1ok}) may have
    varied nationally.  Following shows the mappings of t0/t1 to oktas
    as provided by these routines ({tpt0t1} output):
    10ths clear (t0)   oktas   10ths cover (t1)   oktas
    ----------------   -----   ----------------   -----
                  10       0                  0       0
                   9       1                  1       1
                   8       2                  2       2
                   7       2                  3       2
                   6       3                  4       3
                   5       4                  5       4
                   4       5                  6       5
                   3       6                  7       6
                   2       6                  8       6
                   1       7                  9       7
                   0       8                 10       8
    sdw, 26 Jan 2000.
    Reference:
    Maury, M.F., 1854: Maritime Conference held at Brussels for devising
          a uniform system of meteorological observations at sea, August
          and September, 1853.  Explanations and Sailing Directions to
          Accompany the Wind and Current Charts, 6th Ed., Washington, DC,
          pp. 54-88.

    Parameters
    ----------
    t0 : int
        "proportion of sky clear" in tenths

    Returns
    -------
    ixt0ok : int
        "proportion of sky clear" in oktas

    """
    # check validity of t0
    if t0 not in range(11):
        print('ixt0ok error. illegal t0={}'.format(t0))
        return
    # convert tenths of "sky clear" (t0) to tenths of "sky covered" (t1)
    # (Note: assumption: no known basis in documentation)
    t1 = 10-t0 
    # convert tenths of "sky covered" to oktas
    ixt0ok = ixt1ok(t1)
    return ixt0ok

#=======================================================================
def ixt1ok(t1):
    """
    Converts tenths (of sky covered) (t1), to oktas (eighths of sky
    covered; WMO code 2700).  This implements the mapping of tenths
    to oktas shown below (left-hand columns) from NCDC (1968), section
    4.5, scale 7.  In contrast, the right-hand columns show a reverse
    mapping of "code no." (referring to oktas in the synoptic code)
    back to tenths from Riehl (1947) (the justifications for the two
    approaches are not known):
          oktas  <-  tenths     |    code no.  ->  tenths
          -----      -------    |    --------      -------
            0         0         |        0           0
            1         1         |        1           0
            2         2 or 3    |        2           1
            3         4         |        3           2.5
            4         5         |        4           5
            5         6         |        5           7.5
            6         7 or 8    |        6           9
            7         9         |        7          10 
            8        10         |        8          10
            9        obscured
    Input t1 values must be limited to 0-10; "obscured" is not handled.
    sdw, 26 Jan 2000.
    sdw, 24 Jul 2000: correction of comment.
    References:
    NCDC (National Climatic Data Center), 1968: TDF-11 Reference Manual.
          NCDC, Asheville, NC.
    Riehl, 1947: Diurnal variation of cloudiness over the subtropical
          Atlantic Ocean.  Bull. Amer. Meteor. Soc., 28, 37-40.

    Parameters
    ----------
    t1 : int
        tenths (of sky covered)

    Returns
    -------
    ixt1ok : int
        oktas (eighths of sky
        covered; WMO code 2700)

    """
    ok = [0, 1, 2, 2, 3, 4, 5, 6, 6, 7, 8]
    # check validity of t1
    if t1 not in range(11):
        print('ixt1ok error. illegal t1={}'.format(t1))
        return
    # convert from tenths to oktas
    ixt1ok = ok[t1]
    return ixt1ok

#=======================================================================
#-----temperature conversions-------------------------------------------
#=======================================================================
def fxtftc(tf):
    """
    Convert temperature in degrees Fahrenheit (tc) to degrees Celsius.
    sdw, 26 Jan 2000 (replaces 1 Jul 1998 version from colib5s.01J).
    Reference:
    List, R.J., 1966: Smithsonian Meteorological Tables.
          Smithsonian Institution, Washington, DC, 527 pp.

    Parameters
    ----------
    tf : float
        temperature in degrees Fahrenheit

    Returns
    -------
    fxtftc : float
        temperature in degrees Celsius

    """
    # equation from List (1966), Table 2 (p. 17).
    fxtftc = (5.0/9.0)*(tf-32.0)
    return fxtftc

#-----------------------------------------------------------------------
def fxtctf(tc):
    """
    Convert temperature in degrees Celsius (tc) to degrees Fahrenheit.
    sdw, 26 Jan 2000 (replaces 1 Jul 1998 version from colib5s.01J).
    Reference:
    List, R.J., 1966: Smithsonian Meteorological Tables.
          Smithsonian Institution, Washington, DC, 527 pp.

    Parameters
    ----------
    tc : float
        temperature in degrees Celsius

    Returns
    -------
    fxtctf : float
        temperature in degrees Fahrenheit

    """
    # equation from List (1966), Table 2 (p. 17).
    fxtctf = ((9.0/5.0)*tc)+32.0
    return fxtctf

#-----------------------------------------------------------------------
def fxtktc(tk):
    """
    Convert temperature in Kelvins (tk) to degrees Celsius.
    Adapted from colib5s.01J function {cvtkc} (1984); sdw, 1 Jul 1998.

    Parameters
    ----------
    tk : float
        temperature in Kelvins

    Returns
    -------
    fxtktc : float
        temperature in Celsius

    """
    if tk < 0:
        print('fxtktc error. negative input tk={}'.format(tk))
        return
    fxtktc = tk-273.15
    return fxtktc

#-----------------------------------------------------------------------
def fxtctk(tc):
    """
    Convert temperature in degrees Celsius (tc) to Kelvins.
    Adapted from colib5s.01J function {cvtck} (1984); sdw, 1 Jul 1998.

    Parameters
    ----------
    tc : float
        temperature in degrees Celsius

    Returns
    -------
    fxtctk : float
        temperature in degrees Kelvins

    """
    fxtctk = tc+273.15
    if fxtctk<0:
        print('fxtctk error. negative output={}'.formant(fxtctk))
        return
    return fxtctk

#-----------------------------------------------------------------------
def fxtrtc(tr):
    """
    Convert temperature in degrees Reaumur (tc) to degrees Celsius.
    sdw, 26 Jan 2000 (replaces 1 Jul 1998 version from colib5s.01J).
    Reference:
    List, R.J., 1966: Smithsonian Meteorological Tables.
          Smithsonian Institution, Washington, DC, 527 pp.

    Parameters
    ----------
    tr : float
        temperature in degrees Reaumur

    Returns
    -------
    fxtrtc : float
        temperature in degrees Celsius

    """
    # equation from List (1966), Table 2 (p. 17).
    fxtrtc = (5/4)*tr
    return fxtrtc

#-----------------------------------------------------------------------
def fxtctr(tc):
    """
    Convert temperature in degrees Celsius (tc) to degrees Reaumur.
    sdw, 26 Jan 2000 (replaces 1 Jul 1998 version from colib5s.01J).
    Reference:
    List, R.J., 1966: Smithsonian Meteorological Tables.
          Smithsonian Institution, Washington, DC, 527 pp.

    Parameters
    ----------
    tc : float
        temperature in degrees Celsius

    Returns
    -------
    fxtctr : float
        temperature in degrees Reaumur

    """
    # equation from List (1966), Table 2 (p. 17).
    fxtctr = (4/5)*tc
    return fxtctr

#=======================================================================
#-----wind conversions--------------------------------------------------
#=======================================================================
def fxuvdd(u, v):
    """
    Convert wind vector eastward and northward components (u,v) to
    direction (from) in degrees (clockwise from 0 degrees North).
    Adapted from colib5s.01J function {dduv} (1984); sdw, 1 Jul 1998.

    Parameters
    ----------
    u : float
        wind vector eastward components
    v : float
        wind vector northward components

    Returns
    -------
    fxuvdd : float

    """
    if (u==0 and v==0):
        a = 0
    else:
        a = np.arctan2(v, u)*(180/3.14159265358979323846264338327950288)
    fxuvdd = 270-a
    if fxuvdd>=360:
        fxuvdd = fxuvdd-360
    return fxuvdd

#-----------------------------------------------------------------------
def fxuvvv(u, v):
    """
    Convert wind vector eastward and northward components (u,v) to
    velocity.
    Adapted from colib5s.01J function {vvuv} (1984); sdw, 1 Jul 1998.

    Parameters
    ----------
    u : float
        wind vector eastward components
    v : float
        wind vector northward components

    Returns
    -------
    fxuvvv : float
        velocity

    """
    fxuvvv = np.sqrt(u**2 + v**2)
    return fxuvvv

#-----------------------------------------------------------------------
def fxktms(kt):
    """
    Convert from knots (kt; with respect to the international nautical
    mile) to meters per second (see {tpktms} for details).
    Adapted from colib5s.01J function {cvskm} (1984); sdw, 26 Jun 1998.

    Parameters
    ----------
    kt : float
        knots

    Returns
    -------
    fxktms : float
        meters per second

    """
    fxktms = kt*0.51444444444444444444
    return fxktms

#-----------------------------------------------------------------------
def fxmskt(ms):
    """
    Convert from meters per second (ms) to knots (with respect to the
    international nautical mile) (see {tpktms} for details).
    Adapted from colib5s.01J function {cvsmk} (1984); sdw, 26 Jun 1998.

    Parameters
    ----------
    ms : float
        meters per second

    Returns
    -------
    fxmskt : float
        knots

    """
    fxmskt = ms*1.9438444924406047516
    return fxmskt

#-----------------------------------------------------------------------
def fxk0ms(k0):
    """
    Convert from knots (k0; with respect to the U.S. nautical mile) to
    meters per second (see {tpktms} for details).
    sdw, 26 Jun 1998.

    Parameters
    ----------
    k0 : float
        knots

    Returns
    -------
    fxk0ms : float
        meters per second

    """
    fxk0ms = k0*0.51479111111111111111
    return fxk0ms

#-----------------------------------------------------------------------
def fxmsk0(ms):
    """
    Convert from meters per second (ms) to knots (with respect to the
    U.S. nautical mile) (see {tpktms} for details).
    sdw, 26 Jun 1998.

    Parameters
    ----------
    ms : float
        meters per second

    Returns
    -------
    fxmsk0 : float
        knots

    """
    fxmsk0 = ms*1.9425354836481679732
    return fxmsk0

#-----------------------------------------------------------------------
def fxk1ms(k1):
    """
    Convert from knots (k1; with respect to the Admiralty nautical mile)
    to meters per second (see {tpktms} for details).
    sdw, 26 Jun 1998.

    Parameters
    ----------
    k1 : float
        knots

    Returns
    -------
    fxk1ms : float
        meters per second

    """
    fxk1ms = k1 * 0.51477333333333333333
    return fxk1ms

#-----------------------------------------------------------------------
def fxmsk1(ms):
    """
    Convert from meters per second (ms) to knots (with respect to the
    Admiralty nautical mile) (see {tpktms} for details).
    sdw, 26 Jun 1998.

    Parameters
    ----------
    ms : float
        meters per second

    Returns
    -------
    fxmsk1 : float
        knots

    """
    fxmsk1 = ms*1.9426025694156651471
    return fxmsk1
    
#-----------------------------------------------------------------------
def ixbfkt(bf):
    """
    Convert from Beaufort force 0-12 (bf) to "old" (WMO code 1100)
    midpoint in knots.  From NCDC (1968), conversion scale 5 (sec.
    4.4).  Note: Midpoint value 18 looks questionable, but appeared
    originally in UKMO (1948).
    References:
    NCDC (National Climatic Data Center), 1968: TDF-11 Reference Manual.
          NCDC, Asheville, NC.
    UKMO (UK Met. Office), 1948: International Meteorological Code
          Adopted by the International Meteorological Organisation,
          Washington, 1947 (Decode for the Use of Shipping, effective
          from 1st January, 1949).  Air Ministry, Meteorological Office,
          HM Stationary Office, London, 39 pp.
    sdw, 16 Jun 1998.
    sdw, 26 Jan 2000: complete UKMO reference.
    sdw, 17 Aug 2000: routine name in correct error message.

    Parameters
    ----------
    bf : int
        Beaufort force

    Returns
    -------
    ixbfkt : float
        midpoint in knots

    """
    kt = [0, 2, 5, 9, 13, 18, 24, 30, 37, 44, 52, 60, 68]
    if bf not in range(13):
        print('ixbfkt error.  bf={}'.format(bf))
        return
    ixbfkt = kt[bf]
    return ixbfkt

#-----------------------------------------------------------------------
def fxbfms(bf):
    """
    Convert from Beaufort force 0-12 (bf) to "old" (WMO code 1100)
    midpoint in meters per second.  From Slutz et al. (1985) supp.
    K, Table K5-5 (p. K29).  See {ixbfkt} for additional background.
    Reference:
    Slutz, R.J., S.J. Lubker, J.D. Hiscox, S.D. Woodruff, R.L. Jenne,
          D.H. Joseph, P.M. Steurer, and J.D. Elms, 1985: Comprehensive
          Ocean-Atmosphere Data Data Set; Release 1.  NOAA
          Environmental Research Laboratories, Climate Research
          Program, Boulder, Colo., 268 pp. (NTIS PB86-105723).
    sdw, 16 Jun 1998
    Parameters
    ----------
    bf : int
        Beaufort force
    
    Returns
    -------
    fxbfms : float
        midpoint in meters per second
    """
    ms = [0, 1, 2.6, 4.6, 6.7, 9.3, 12.3, 15.4, 19, 22.6, 26.8, 30.9, 35]
    if bf not in range(13):
        print('fxbfms error.  bf={}'.format(bf))
        return
    fxbfms = ms[bf]
    return fxbfms

#-----------------------------------------------------------------------
def ix32dd(c32, dc, imiss):
    """
    Convert 4-character 32-point wind direction abbreviation c32 into
    degrees, or return imiss if unrecognized; also return numeric code
    1-32 (or imiss) in dc (see {ixdcdd} for background).  Recognized
    abbreviations are in cwd, with these characteristics: left-justified,
    upper-case, with trailing blank fill, and where "X" stands for "by".
    NOTE: No constraint is placed on imiss (it could overlap with data).
    sdw, 17 Aug 2000.

    Parameters
    ----------
    c32 : string
        4-character 32-point wind direction abbreviation
    dc : float
        degrees
    imiss : float
        option for missing value

    Returns
    -------
    ix32dd

    """
    cwd = ['NXE ','NNE ','NEXN','NE  ','NEXE','ENE ','EXN ','E   ',
           'EXS ','ESE ','SEXE','SE  ','SEXS','SSE ','SXE ','S   ',
           'SXW ','SSW ','SWXS','SW  ','SWXW','WSW ','WXS ','W   ',
           'WXN ','WNW ','NWXW','NW  ','NWXN','NNW ','NXW ','N   ']
    ix32dd = imiss
    for j in range(32):
        if c32==cwd[j]:
            ix32dd = ixdcdd[j, imiss]
            dc = j
            return
        
    return ix32dd

#-----------------------------------------------------------------------3456789
def ixdcdd(dc, imiss):
    """
    Convert 32-point wind direction numeric code dc into degrees, or
    return imiss if dc is out of range 1-32.  Release 1, Table F2-1
    defines the mapping of code dc to degrees in dwd.
    NOTE: No constraint is placed on imiss (it could overlap with data).
    sdw, 17 Aug 2000.

    Parameters
    ----------
    dc : int
        32-point wind direction numeric code
    imiss : float
        option for missing value

    Returns
    -------
    ixdcdd : float
        wind direction in degrees

    """
    dwd = [11, 23, 34, 45, 56, 68, 79, 90, 101, 113, 124, 135, 146, 158, 169,
           180, 191, 203, 214, 225, 236, 248, 259, 270, 281, 293, 304, 315, 
           326, 338, 349, 360]
    if dc in range(32):
        ixdcdd = dwd[dc]
    else:
        ixdcdd = imiss
    return ixdcdd
