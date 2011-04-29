"""Utilities for fetching and plotting DWAF real-time data.

This module contains some simple functions to make it easier
to read and plot the data from GRIB(version 1) files produced
by SAWS Unified Model. The module relies on Wesley Ebisuzaki's
wgrib programme being somewhere on your systems path. If you
don't have wgrib it can be obtained from:

http://www.cpc.ncep.noaa.gov/products/wesley/wgrib.html

"""
##
##    berg_dischargee.py
##
##    Based on the file
##
##    merrimack_discharge.py
##
##    Created by Robert Hetland on 2006-04-20.
##    Copyright (c) 2006 Texas A&M University. All rights reserved.
##
##    and liberally edited by:
##    Scott Sinclair 2006-09-30
##    Copyright (c) 2006 Satelitte Application and Hydrology Group
##    University of KZN, South Africa. All rights reserved.
##

from numpy import *
from dateutil.parser import parse
from datetime import datetime
import urllib2
import pylab as pl
from matplotlib.font_manager import FontProperties
import matplotlib.mathtext
##import sys
from matplotlib.dates import DayLocator, HourLocator, DateFormatter


proxy_default = {'user' : 'user',
                 'pass' : 'pass',
                 'host' : 'DBNPROXY1.UKZN.AC.ZA',
                 'port' : 8080
}

station_name = {'Berg at Bergriviershoek': 'G1H004H3T',
                'Ash at tunnel from Katse Dam': 'C8H036',
                'Vaal at Bloukop': 'C1H007RAD',
                'Nuwejaarspr at Sterkfontein Dam': 'C8R003D',
                'Liebenbergsvlei at Frederiksdal (G)': 'C8H026GPRS',
                'Mlazi at Eshowe': 'W1H004EC'}

class discharge(object):

    def __init__(self, station_desc, proxy_info=proxy_default, \
                 source='real-time', savefile=None):
        """Load data from http://www.dwaf.gov.za/Hydrology/ and plot.

        To find your station-id, visit:
        Initialize class:
        >>> d = discharge(file)  # where file is a datafile from
        >>> d = discharge(site-id, source='recent', savefile=None)
            # load data from web, given a site id
            # data = 'recent' or 'historical'
            # If savefile is given, the data will be saved to the given filename

        methods:
        >>> yearday, qmean, qstd = d.annual_stats(ref_year=1970)
        >>> yearday, q = d.get_year(year=1970, ref_year=1970)

        """
        station_id = station_name[station_desc]

        try:
            f = open(station_id)
            lines = open(station_id).readlines()
            f.close()
        except IOError:
            url = 'http://www.dwaf.gov.za/Hydrology/RTData.aspx?Station=%s&Type=Data' % station_id

            # build a new opener that uses a proxy requiring authorization
            proxy_support = urllib2.ProxyHandler({"http" : \
            "http://%(user)s:%(pass)s@%(host)s:%(port)d" % proxy_info})

            opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)

            # install it
            urllib2.install_opener(opener)

            # use it
            lines = urllib2.urlopen(url).readlines()
            if savefile is not None:
                f = open(savefile,'w')
                for line in lines:
                    f.write(line)
                    f.write('\n')
                f.close()
            for line in lines:
                if 'error' in line:
                    raise IOError('File or Station ID not found')

        line = lines.pop(0)
        # get discharge
        # format: ????
        elements = line.split('<br>')

        data = [];

        for elem in elements:
            if elem[0] != '<' and elem[0] != 'C' and elem[0] != '*':
                data.append(elem.split())

        q = []; date = []

        for x in data:
            yr, mnth, dy = x[0].split('-')
            hr, mn = x[1].split(':')
            dt = datetime(int(yr), int(mnth), int(dy), int(hr), int(mn))
            date.append(dt)
            q.append(float(x[3]))

        self.q = asarray(q)
        self.date = asarray(date)
        self.jd = asarray(pl.date2num(self.date))
        self.station_desc = station_desc
        self.station_id = station_id

def plot_dwaf_data(realtime, file_name='data_plot.png', gauge=True):
    x = pl.date2num(realtime.date)
    y = realtime.q

    pl.clf()
    pl.figure(figsize=(7.5, 4.5))
    pl.rc('text', usetex=True)# TEX fonts
    pl.plot_date(x,y,'b-',linewidth=1)
    pl.grid(which='major')
    pl.grid(which='minor')

    if gauge:
        pl.ylabel(r'Flow rate (m$^3$s$^{-1}$)')
        title = 'Real-time flow -- %s [%s]' % (realtime.station_id[0:6], realtime.station_desc)
    else:
        title = 'Real-time capacity -- %s [%s]' % (realtime.station_id[0:6], realtime.station_desc)
        pl.ylabel('Percentage of F.S.C')

    labeled_days = DayLocator(interval=3)
    ticked_days = DayLocator()
    dayfmt = DateFormatter('%d/%m/%Y')

    ax = pl.gca()
    ax.xaxis.set_major_locator(labeled_days)
    ax.xaxis.set_major_formatter(dayfmt)
    ax.xaxis.set_minor_locator(ticked_days)

    pl.xticks(fontsize=10)
    pl.yticks(fontsize=10)

    pl.title(title, fontsize=14)

    pl.savefig(file_name, dpi=100)
