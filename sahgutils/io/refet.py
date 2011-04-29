"""Compute Hourly ET based on FAO56.

Compute the hourly reference crop ET in mm using the FAO
Penman-Monteith algorithm described in FAO56. The input data can be
Numpy arrays, representing the Meteorological variables at many
locations.

Allen R.G., Pereira L.S., Raes D. and Smith M., (1998), 'Crop
evapotranspiration - Guidelines for computing crop water
requirements', FAO Irrigation and drainage paper 56, Rome.

FAO56: http://www.fao.org/docrep/X0490E/x0490e00.HTM

"""
import numpy as np
from numpy import sin
from numpy import cos
from numpy import exp
from numpy import pi
from numpy import sqrt

def vapour_pressure_slope(T):
    """Compute the slope of the vapour pressure curve.

    Use's equation 13 from FAO56 with the mean temperature for the hour
    in degrees Centigrade as input. Output units are in kPa/degree C.
    """
    a = T + 237.3
    b = saturation_vapour_pressure(T)

    Delta = (4098*b)/(a**2)

    return Delta

def psychrometric_constant(z):
    """Compute the value of the psychrometric constant.

    Estimated from equation 8 FAO56. The input data are the elevations of
    the locations above sea level in metres. Values used for the physical
    data are:

    Latent heat of vapourization = 2.45 MJ kg$^{-1}$
    Specific heat @ constant pressure = 1.013$\times$10 3$^{-3}$ MJ kg$^{-1}$ $^{\circ}$C$^{-1}$
    Ratio of Molecular weight dry/wet air = 0.622

    """
    P = 101.3*(((293 - 0.0065*z)/293)**5.26)

    return 0.000665*P

def saturation_vapour_pressure(T):
    """Compute the saturation vapour pressure.

    Uses equation 11 from FAO56.
    """
    a = T + 237.3

    return 0.6108*exp((17.27*T)/a)

def actual_vapour_pressure(T, RH):
    """Compute the actual vapour pressure.

    Uses equation 54 from FAO56.
    """
    a = saturation_vapour_pressure(T)

    return a*(RH/100.0)

def vapour_pressure_deficit(T, RH):
    """Compute the vapour pressure deficit."""
    return saturation_vapour_pressure(T) - actual_vapour_pressure(T, RH)

def julian_day(day, month, year):
    """Compute the julian day number from the year, month and day."""

    J = np.floor((275/9.0)*month - 30 + day)
    J = J - 2

    J[month < 3] += 2

##    if (year % 400) == 0:
##        leapyear = True
##    elif (year % 100) == 0:
##        leapyear = False
##    elif (year % 4) == 0:
##        leapyear = True
##    else:
##        leapyear = False
    leapyear = False

    J[leapyear & (month > 2)] += 1

    return J

##    J = int(275*month/9.0 - 30 + day) - 2
##
##    if month < 3:
##        J = J + 2
##
##    if (year % 400) == 0:
##        leapyear = True
##    elif (year % 100) == 0:
##        leapyear = False
##    elif (year % 4) == 0:
##        leapyear = True
##    else:
##        leapyear = False
##
##    if leapyear and month > 2:
##        J = J + 1
##
##    return J

def latitude_radians(lat):
    """Convert latitude in decimal degrees to radians.

    Uses equation 22 from FAO56.
    """
    return (pi/180.0)*lat

def inv_rel_earth_sun_dist(J):
    """Compute the inverse relative earth-sun distance.

    Uses equation 23 from FAO56.
    """
    return 1 + 0.033*cos(((2*pi)/365.0)*J)

def solar_declination(J):
    """Compute the solar declination.

    Uses equation 24 from FAO56.
    """
    return 0.409*sin(((2*pi)/365.0)*J - 1.39)

def solar_time_correction(J):
    """Compute the seasonal solar time correction.

    Uses equations 32 and 33 from FAO56.
    """
    b = (2*pi*(J - 81))/364.0

    return 0.1645*sin(2*b) - 0.1255*cos(b) - 0.025*sin(b)

def start_solar_time_angle(omega, period):
    """Compute the solar time angle at the midpoint of the period.

    Uses equation 29 from FAO56.
    """
    return omega - (pi*period)/24

def end_solar_time_angle(omega, period):
    """Compute the solar time angle at the midpoint of the period.

    Uses equation 30 from FAO56.
    """
    return omega + (pi*period)/24

def midpoint_solar_time_angle(tm, Lz, Lm, Sc):
    """Compute the solar time angle at the midpoint of the period.

    Uses equation 31 from FAO56.
    """
    return (pi/12)*((tm + 0.06667*(Lz - Lm) + Sc) - 12)

def extraterrestrial_radiation(dr, delta, phi, omega, omega1, omega2):
    """Compute the extraterrestrial radiation.

    Uses equations 25 &  28 from FAO56.
    """
    o1 = np.asarray(omega1)
    o2 = np.asarray(omega2)
    a = (o2 - o1)*sin(phi)*sin(delta)
    b = cos(phi)*cos(delta)*(sin(o2) - sin(o1))

    Ra = ((12*60)/pi)*0.082*dr*(a + b)
    
    # test sunset time angle
    omega_s = np.arccos(-np.tan(phi)*np.tan(delta))
    Ra[(omega < -omega_s) | (omega > omega_s)] = 0

    return Ra

def clear_sky_radiation(Ra, z):
    """Compute the clear sky radiation.

    Uses equation 37 from FAO56.
    """
    return (0.75 + 0.00002*z)*Ra

def net_sw_radiation(Rs):
    """Compute the net short wave radiation.

    Uses equation 38 from FAO56 with an albedo value of 0.23 based on the
    definition of the reference crop.
    """
    return 0.77*Rs

def net_outgoing_lw_radiation(T, ea, Rs, Rs0):
    """Compute the net outgoing long wave radiation.

    Uses equation 39 from FAO56. However, the ratio of Rs/Rs0 has been fixed at
    a value of 0.8 during the night. This should be modiifed to use the ratio
    calculated 2-3 hours before sunset as suggested in FAO56.
    """
    a = 2.043E-10*((T + 273.16)**4)
    b = 0.34 - 0.14*sqrt(ea)
    
    c = np.empty(Rs.shape)
    c[Rs0 > 0] = Rs[Rs0 > 0]/Rs0[Rs0 > 0]
    c[Rs0 == 0] = 0.8 # night, needs work!!!!

    # Rs/Rs0 must be <= 1
    c[c > 1] = 1.0
    c = 1.35*c - 0.35

    return a*b*c

def net_radiation(Rns, Rnl):
    """Compute the net radiation.

    Uses equation 40 from FAO56.
    """
    return Rns - Rnl

def soil_heat_flux(Rn, Rs):
    """Compute the soil heat flux.

    Uses equations 45 and 46 from FAO56. The distinction between nightime and
    daylight is made on the basis of the incoming solar radiation estimate. If
    Rs is below a threshold value of 0.05 MJm^-2hr^-1 then nightime is assumed.
    This threshold is fairly arbitrary and could be chosen in a more sensible
    manner e.g. based on the sun angle 'omega_s'.
    """
    threshold = 0.05
    
    G = 0.1*Rn # daylight
    G[Rs < threshold] = 0.5*Rn[Rs < threshold] # nighttime
    
    return G

def compute_ET(Delta, Rn, G, gamma, T, e0, ea, u2):
    """Compute Hourly ET based on FAO56

    Compute the hourly reference crop ET in mm using the FAO Penman-Monteith
    algorithm described in FAO56. The input data can be Numpy arrays,
    representing the Meteorological variables at many locations.

    FAO56: http://www.fao.org/docrep/X0490E/x0490e00.HTM

    """
    a = 0.408*Delta*(Rn - G)
    b = gamma*(37.0/(T + 273))*u2*(e0 - ea)
    c = Delta + gamma*(1 + 0.34*u2)

    return (a + b)/c

def reference_ET(temp, elev, rel_hum, day, month, year,
                                lats, tm, Lz, Lm, period, Rs, u2):
    """Compute ref ET.

    This function is a wrapper to make the module easier to use.

    """
    temp = np.asarray(temp)
    elev = np.asarray(elev)
    rel_hum = np.asarray(rel_hum)
    day = np.asarray(day)
    month = np.asarray(month)
    year = np.asarray(year)
    lats = np.asarray(lats)
    tm = np.asarray(tm)
    Lz = np.asarray(Lz)
    Lm = np.asarray(Lm)
    period = np.asarray(period)
    Rs = np.asarray(Rs)
    u2 = np.asarray(u2)

    # compute ETr
    Delta = vapour_pressure_slope(temp)
    gamma = psychrometric_constant(elev)
    e0 = saturation_vapour_pressure(temp)
    ea = actual_vapour_pressure(temp, rel_hum)
    j_day = julian_day(day, month, year)
    phi = latitude_radians(lats)
    dr = inv_rel_earth_sun_dist(j_day)
    delta = solar_declination(j_day)
    Sc = solar_time_correction(j_day)
    omega = midpoint_solar_time_angle(tm, Lz, Lm, Sc)
    omega1 = start_solar_time_angle(omega, period)
    omega2 = end_solar_time_angle(omega, period)
    Ra = extraterrestrial_radiation(dr, delta, phi, omega, omega1, omega2)
    Rs0 = clear_sky_radiation(Ra, elev)
    Rns = net_sw_radiation(Rs)
    Rnl = net_outgoing_lw_radiation(temp, ea, Rs, Rs0)
    Rn = net_radiation(Rns, Rnl)
    G = soil_heat_flux(Rn, Rs)
    ETr = compute_ET(Delta, Rn, G, gamma, temp, e0, ea, u2)
    
    return ETr

def test():
    # Check that the code produces results that match those provided
    # in FAO56 example 19
    fao_Delta = np.array([0.22, 0.358])
    fao_gamma = np.array([0.0673, 0.0673])
    fao_e0 = np.array([3.78, 6.625])
    fao_ea = np.array([3.402, 3.445])
    fao_e_def = np.array([0.378, 3.18])
    fao_j_day = np.array([274, 274])
    fao_phi = np.array([0.283, 0.283])
    fao_dr = np.array([1.0001, 1.0001])
    fao_delta = np.array([-0.0753, -0.0753])
    fao_Sc = np.array([0.1889, 0.1889])
    fao_omega = np.array([-2.46, 0.682])
    fao_omega1 = np.array([0, 0.5512]) # doesn't exist at night!
    fao_omega2 = np.array([0, 0.813]) # doesn't exist at night!
    fao_Ra = np.array([0, 3.543]) # negligable incoming rad at night!
    fao_Rs0 = np.array([0, 2.658])
    fao_Rns = np.array([0, 1.887])
    fao_Rnl = np.array([0.1, 0.137])
    fao_Rn = np.array([-0.1, 1.749])
    fao_G = np.array([-0.05, 0.175])
    fao_ETr = np.array([0.0, 0.63])

    temp = np.array([28, 38])
    elev = np.array([8, 8])
    rel_hum = np.array([90, 52])
    day = np.array([1, 1])
    month = np.array([10, 10])
    year = np.array([2006, 2006])
    lat = np.array([16.22, 16.22])
    tm = np.array([2.5, 14.5])
    Lz = np.array([15, 15])
    Lm = np.array([16.25, 16.25])
    period = np.array([1, 1])
    Rs = np.array([0, 2.45])
    u2 = np.array([1.9, 3.3])

    # compute
    Delta = vapour_pressure_slope(temp)
    gamma = psychrometric_constant(elev)
    e0 = saturation_vapour_pressure(temp)
    ea = actual_vapour_pressure(temp, rel_hum)
    j_day = julian_day(day, month, year)
    phi = latitude_radians(lat)
    dr = inv_rel_earth_sun_dist(j_day)
    delta = solar_declination(j_day)
    Sc = solar_time_correction(j_day)
    omega = midpoint_solar_time_angle(tm, Lz, Lm, Sc)
    omega1 = start_solar_time_angle(omega, period)
    omega2 = end_solar_time_angle(omega, period)
    Ra = extraterrestrial_radiation(dr, delta, phi, omega, omega1, omega2)
    Rs0 = clear_sky_radiation(Ra, elev)
    Rns = net_sw_radiation(Rs)
    Rnl = net_outgoing_lw_radiation(temp, ea, Rs, Rs0)
    Rn = net_radiation(Rns, Rnl)
    G = soil_heat_flux(Rn, Rs)
    ETr = compute_ET(Delta, Rn, G, gamma, temp, e0, ea, u2)

    e_def = vapour_pressure_deficit(temp, rel_hum)

    print 'Vapour pressure slope:            ', Delta
    print 'Psychrometric constant:           ', gamma
    print 'Saturation vapour pressure:       ', e0
    print 'Actual vapour pressure:           ', ea
    print 'Vapour pressure deficit:          ', e_def
    print 'Julian day:                       ', j_day
    print 'Latitude in radians:              ', phi
    print 'Inv. rel. earth-sun distance:     ', dr
    print 'Solar declination:                ', delta
    print 'Solar time correction:            ', Sc
    print 'Midpoint solar time angle:        ', omega
    print 'Start solar time angle:           ', omega1
    print 'End solar time angle:             ', omega2
    print 'Extraterrestrial radiation:       ', Ra
    print 'Clear sky radiation:              ', Rs0
    print 'Net short wave radiation:         ', Rns
    print 'Net outgoing long wave radiation: ', Rnl
    print 'Net radiation:                    ', Rn
    print 'Soil heat flux:                   ', G
    print 'Reference crop ET:                ', ETr

    print '\n\nErrors relative to FAO56 results-----------------------------'
    print 'Vapour pressure slope:            ', np.round(Delta, 3) - fao_Delta
    print 'Psychrometric constant:           ', np.round(gamma, 4) - fao_gamma
    print 'Saturation vapour pressure:       ', np.round(e0, 3) - fao_e0
    print 'Actual vapour pressure:           ', np.round(ea, 3) - fao_ea
    print 'Vapour pressure deficit:          ', np.round(e_def, 3) - fao_e_def
    print 'Julian day:                       ', np.round(j_day, 0) - fao_j_day
    print 'Latitude in radians:              ', np.round(phi, 4) - fao_phi
    print 'Inv. rel. earth-sun distance:     ', np.round(dr, 4) - fao_dr
    print 'Solar declination:                ', np.round(delta, 4) - fao_delta
    print 'Solar time correction:            ', np.round(Sc, 4) - fao_Sc
    print 'Midpoint solar time angle:        ', np.round(omega, 3) - fao_omega
    print 'Start solar time angle:           ', np.round(omega1, 4) - fao_omega1
    print 'End solar time angle:             ', np.round(omega2, 4) - fao_omega2
    print 'Extraterrestrial radiation:       ', np.round(Ra, 3) - fao_Ra
    print 'Clear sky radiation:              ', np.round(Rs0, 3) - fao_Rs0
    print 'Net short wave radiation:         ', np.round(Rns, 3) - fao_Rns
    print 'Net outgoing long wave radiation: ', np.round(Rnl, 3) - fao_Rnl
    print 'Net radiation:                    ', np.round(Rn, 3) - fao_Rn
    print 'Soil heat flux:                   ', np.round(G, 3) - fao_G
    print 'Reference crop ET:                ', np.round(ETr, 2) - fao_ETr

def test_wrapper():
    temp = [28, 38]
    elev = [8, 8]
    rel_hum = [90, 52]
    day = [1, 1]
    month = [10, 10]
    year = [2006, 2006]
    lats = [16.22, 16.22]
    tm = [2.5, 14.5]
    Lz = [15, 15]
    Lm = [16.25, 16.25]
    period = [1, 1]
    Rs = [0, 2.45]
    u2 = [1.9, 3.3]

    # compute
    ETr = reference_ET(temp, elev, rel_hum, day, month, year,
                                            lats, tm, Lz, Lm, period, Rs, u2)
                                            
    print '\n\nWrapped Reference crop ET:                ', ETr

if __name__ == '__main__':
    print 'Comparing results to FAO56 Example 19...\n'
    test()
    test_wrapper()

