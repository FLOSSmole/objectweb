# -*- coding: utf-8 -*-
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# License: GPLv2
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

import urllib.request
from bs4 import BeautifulSoup
import sys
import pymysql
import datetime

datasource_id = sys.argv[1]
password      = sys.argv[2]

projectListURL = 'https://forge.ow2.org/softwaremap/full_list.php'
countT = 1
count = 0
page = 1
i = 0

# establish database connection: ELON
'''
try:
    db = pymysql.connect(host='grid6.cs.elon.edu',
                        database='objectweb',
                        user='megan',
                        password=password,
                        use_unicode=True,
                        charset='utf8')
except pymysql.Error as err:
    print(err)
else:
    cursor = db.cursor()
'''

# establish database connection: SYR
try:
    db1 = pymysql.connect(host='flossdata.syr.edu',
                        database='objectweb',
                        user='megan',
                        password=password,
                        use_unicode=True,
                        charset='utf8')
except pymysql.Error as err:
    print(err)
else:
    cursor1 = db1.cursor()


# Get page that lists all projects
try:
    projectListPage = urllib.request.urlopen(projectListURL)
except urllib.error.URLError as e:
    print(e.reason)
else:
    urlStem = 'http://forge.objectweb.org/projects/'
    insertProjectQuery = 'INSERT INTO ow_projects ' + \
                         '(proj_unixname, ' + \
                         'url,' + \
                         'proj_long_name,' + \
                         'datasource_id,' + \
                         'date_collected)' + \
                         'VALUES (%s,%s,%s,%s,%s)'
                                     
    soup = BeautifulSoup(projectListPage, "lxml")
    # Get all project names listed on that page
    for i in soup.findAll('select', attrs={'name': 'navigation'}):
        
        projectOptions = i.findAll('option')
        # For each project, pull out its basic facts and insert into database
        for option in projectOptions:
            projectURL = option.get('value')
            projectLongName = option.text

            if projectURL and urlStem in projectURL:
                projectShortName = projectURL[len(urlStem):]
                print('working on', projectShortName)
                try:
                    cursor1.execute(insertProjectQuery, 
                         (projectShortName, 
                          projectURL,
                          projectLongName,
                          datasource_id,
                          datetime.datetime.now()))
                    db1.commit()
                except pymysql.Error as err:
                    print(err)
                    db1.rollback() 
            
