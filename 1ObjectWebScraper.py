# -*- coding: utf-8 -*-
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# License: GPLv3
# 
# Contribution from:
# Caroline Frankel
#
# We're working on this at http://flossmole.org - Come help us build
# an open and accessible repository for data and analyses for free and open
# source projects.
#
# If you use this code or data for preparing an academic paper please
# provide a citation to:
#
# Howison, J., Conklin, M., & Crowston, K. (2006). FLOSSmole:
# A collaborative repository for FLOSS research data and analyses.
# International Journal of Information Technology and Web Engineering, 1(3),
# 17–26.
#
# and
#
# FLOSSmole: a project to provide research access to
# data and analyses of open source projects.
# Available at http://flossmole.org
#
################################################################
# usage:
# python 1ObjectWebScraper.py <datasource_id> <password>
#
# purpose:
# get master list of ObjectWeb projects and add basic facts to database
################################################################

from bs4 import BeautifulSoup
import sys
import pymysql
import datetime
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

datasource_id = sys.argv[1]
password      = sys.argv[2]

# establish database connection: SYR
db = pymysql.connect(host='flossdata.syr.edu',
                     user='',
                     passwd='',
                     db='',
                     use_unicode=True,
                     charset="utf8mb4")
cursor = db.cursor()

insertQuery = 'INSERT INTO ow_projects  \
                         (proj_unixname,  \
                         url, \
                         proj_long_name, \
                         datasource_id, \
                         date_collected) \
                         VALUES (%s,%s,%s,%s,%s)'

# set up headers
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

# Get page that lists all projects
try:
    projectListURL = 'https://forge.ow2.org/softwaremap/full_list.php'

    req = urllib2.Request(projectListURL, headers=hdr)
    projectListPage = urllib2.urlopen(req).read()  # this is a HTML

    soup = BeautifulSoup(projectListPage, "html.parser")
    td = soup.find_all('select', attrs={'name': 'navigation'})

    urlStem = 'http://forge.objectweb.org/projects/'

    for line in td:
        projectOptions = line.find_all('option')

        for option in projectOptions:
            projectURL = option.get('value')
            projectLongName = option.text

            if projectURL and urlStem in projectURL:
                projectShortName = projectURL[len(urlStem):

                print('working on', projectShortName)
                try:
                    cursor.execute(insertProjectQuery, 
                         (projectShortName, 
                          projectURL,
                          projectLongName,
                          datasource_id,
                          datetime.datetime.now()))
                    db.commit()
                except pymysql.Error as err:
                    print(err)
                    db.rollback() 
except urllib.error.URLError as e:
    print(e.reason)
