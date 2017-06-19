#!/usr/bin/env python
'''
This code uses our modified Tor to download objects from a destination. We modified the Tor to use only the exit relays that *only* suppert exit to port 80 and 443. We want to measure whether using the port specification based on the traffic improves the performance or not. For exmaple, how selecting the circuti's exit nodes among those relays that only support ports 80 and 443 affects the performance.

The code launchs the Tor, starts downloading the object from the given address, kills the Tor process, and starts the proccess again.

'''


SOCKS_PORT = '9050'
controlport = '9051'
CONNECTION_TIMEOUT = 40
torpath = '/home/isec/projects/test-tor/tor-0.2.6.10/src/or/tor' # path to the executable Tor
dest_address = 'http://vhost2.hansenet.de/1_mb_file.bin' # the destination address


import io
import pycurl, time
import psutil
import stem.process
import stem.control as Controller
from stem.util import term
import matplotlib.pyplot as plt
import os,pylab
from math import sqrt
from matplotlib2tikz import save as tikz_save
import matplotlib
import numpy as np
from sets import Set, ImmutableSet



def cf(d): return pylab.arange(1.0,float(len(d))+1.0)/float(len(d))
def getcdf(data, shownpercentile=0.99, maxpoints=100000.0):
    data.sort()
    frac = cf(data)
    k = len(data)/maxpoints
    x, y, lasty = [], [], 0.0
    for i in xrange(int(round(len(data)*shownpercentile))):
        if i % k > 1.0: continue
        assert not np.isnan(data[i])
        x.append(data[i])
        y.append(lasty)
        x.append(data[i])
        y.append(frac[i])
        lasty = frac[i]
    return x, y





def print_bootstrap_lines(line):
  if "Bootstrapped " in line:
    print(term.format(line, term.Color.BLUE))


def launch_tor_service():
    """Launch Tor service and return the process."""
    tor_process = stem.process
    PROCNAME = "tor"
    for proc in psutil.process_iter():
        # check whether the process name matches
        if proc.name() == PROCNAME:
            proc.kill()

    print("Tor config: %s" % {'controlport': controlport, 'socksport': SOCKS_PORT})
    # the following may raise, make sure it's handled
    tor_process = stem.process.launch_tor_with_config(
        config={'controlport': controlport, 'socksport': SOCKS_PORT},
        init_msg_handler=print_bootstrap_lines,
        tor_cmd= torpath
    )
    return tor_process


def query(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """

  output = io.BytesIO()

  query = pycurl.Curl()
  query.setopt(pycurl.URL, url)
  query.setopt(pycurl.PROXY, 'localhost')
  query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
  query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
  query.setopt(pycurl.WRITEFUNCTION, lambda x: None)
  query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)

  try:
    query.perform()
    return output.getvalue()
  except pycurl.error as exc:
    return "Unable to reach %s (%s)" % (url, exc)


# Start an instance of Tor configured to only exit through Russia. This prints
# Tor's bootstrap information as it starts. Note that this likely will not
# work if you have another Tor instance running.


def test():
    cnt = 0
    file_ = open("tor-test.log", 'w')
    file_.close()
    while (cnt < 500):
        print(term.format("Starting Tor:\n", term.Attr.BOLD))
        try:
            time.sleep(1)
            tor_process = launch_tor_service()
            '''

            tor_process = stem.process.launch_tor_with_config(
              config = {
                'SocksPort': str(SOCKS_PORT),
                'ExitNodes': '{ru}',
                'GeoIPFile': '/home/isec/projects/test-tor/tor-0.2.6.10/src/config\geoip',
                'FascistFirewall':'1',
                'GeoIPv6File': '/home/isec/projects/test-tor/tor-0.2.6.10/src/config\geoip6'
              },
              init_msg_handler = print_bootstrap_lines,
            )
            '''
            print(term.format("\nChecking our endpoint:\n", term.Attr.BOLD))
            time1 = time.time()
            print(term.format(query(dest_address), term.Color.BLUE))
            t =  time.time() - time1
            tor_process.kill()  # stops tor
            file_ = open("tor-test.log", 'a')
            file_.write('{0}:\n'.format(t))
            print 'download:{0}:\t:time:{1}'.format(cnt,t)
            cnt += 1
            file_.close()
        except:
            cnt += 1



def plotcdf():
    '''
    Plot the cdf of download times
    '''


    file_ = open('tor-test80-443.log', 'r')
    port80_443 = []
    for line in file_:
        port80_443.append(float(line.split(':')[0]))
    file_.close()
    x, y = getcdf(port80_443)
    plt.plot(x, y, color='r', linestyle='-.',label='P80 P443 ({0})'.format(len(port80_443)))

    file_ = open('tor-test.log', 'r')
    port = []
    for line in file_:
        port.append(float(line.split(':')[0]))
    file_.close()
    x, y = getcdf(port)
    plt.plot(x, y, color='g', linestyle='-.',label='all ({0})'.format(len(port)))
    plt.title("CDF")
    plt.xlabel("Download time")
    plt.ylabel("Fraction")
    plt.legend(loc='best')
    plt.savefig('cdf.jpg', format='jpg')
    plt.close()


plotcdf()

