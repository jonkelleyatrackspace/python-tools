#!/usr/bin/env python
# Jon Kelley May 5, 2014
#  Used to send server-status from Apache stats into graphite.
#  Collects worker operations. Ideally run every minute by cron.


import urllib2 # Metric Calc
from collections import defaultdict # Metric Calc
import socket, time # For graphite
import re # For hostname hax 

APPGROUP="appname"
STATUS_URL = 'https://' + socket.gethostname() + '/server-status'
CARBON_SERVER = 'graphite-host'
CARBON_PORT = 2003

def retrieve_page(stat_url):
  """ Returns a dictionary with the main status stub and the auto status page """
  # Main
  req = urllib2.Request(stat_url)
  response = urllib2.urlopen(req)

  return response.read()

def calc_metric_autostatus(url):
  """ Returns json object with metrics for main status """
  status = retrieve_page(url + "?auto").splitlines()

  # Metrics we wish to publish.
  stats = {}

  linenum = 0
  for line in status:
    linenum += 1

    if linenum == 1: # BusyWorkers
      res = line.split(':')
      # Expose busyworker metric
      stats[res[0]] = res[1]
    elif linenum == 2: # IdleWorkers
      res = line.split(':')
      # Expose idleworker metric
      stats[res[0]] = res[1]
    elif linenum == 3: # Scoreboard
      res = line.split(':')

      # Put the scoreboard into a dictionary counter.
      workercounts = defaultdict(int)
      for i in res[1]:
        workercounts[i] += 1

      # Expose each count as a named metric.
      for k,v in workercounts.iteritems():
        if k == "_":
          stats['waiting_for_connection'] = v
        elif k == "S":
          stats['starting_up'] = v
        elif k == "R":
          stats['reading_request'] = v
        elif k == "W":
          stats['sending_reply'] = v
        elif k == "K":
          stats['keepalive_read'] = v
        elif k == "D":
          stats['dns_lookup'] = v
        elif k == "C":
          stats['closing_connection'] = v
        elif k == "L":
          stats['logging'] = v
        elif k == "G":
          stats['graceful_finishing'] = v
        elif k == "I":
          stats['idle_worker_cleanup'] = v

  return stats
def send_metric(name,value):
  """ Sends a metric to graphite over udp """
  value = str(value)
  epoch = int(time.time())
  PREFIX = "scripts."+APPGROUP+".server_status." + return_sane_hostname() + "."
  name = PREFIX + name

  message = '%s %s %d\n' % (name, value, epoch)

  print 'sending message:\n%s' % message
  sock = socket.socket()
  sock.connect((CARBON_SERVER, CARBON_PORT))
  sock.sendall(message)
  sock.close()

def return_sane_hostname():
  """ Returns a hostname with graphite compatible namespace """
  result = re.sub('[^a-zA-Z0-9\-]', '_', socket.gethostname())
  return result

if __name__ == "__main__":
  metrics = calc_metric_autostatus(STATUS_URL)

  for k,v in metrics.iteritems():
    send_metric(name=k,value=v)


