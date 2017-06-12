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
# python 2OWProjectCollector.py <datasource_id> <password>
# purpose:
# grab project page and parse out interesting bits, write those to db
################################################################

import urllib.request
import re
import sys
import pymysql
import datetime

datasource_id = sys.argv[1]
password      = sys.argv[2]


# establish database connection: SYR
try:
    db = pymysql.connect(host='flossdata.syr.edu',
                     user='',
                     passwd='',
                     db='',
                     use_unicode=True,
                     charset="utf8mb4")
    cursor = db.cursor()
except pymysql.Error as err:
    print(err)

# Get list of all projects & urls from the database
selectQuery = 'SELECT proj_unixname, url FROM ow_projects ' \
              'WHERE datasource_id=%s ORDER BY 1'
updateProjectQuery = 'UPDATE ow_projects ' \
                     'SET ' \
                     'date_registered = %s,' \
                     'date_collected = %s' \
                     'WHERE proj_unixname = %s' \
                     'AND datasource_id = %s;'
try:
    cursor.execute(selectQuery, (datasource_id))
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        currentProject = project[0]
        projectOWUrl = project[1]
        print('working on', currentProject)
        try:
            projectPage = urllib.request.urlopen(projectOWUrl)
            myPage = projectPage.read().decode('utf-8')
            results = re.findall('Registered:&nbsp;(.*?)\s(\d\d:\d\d)', myPage)

            if results:
                regDate = results[0][0] + ' ' + results[0][1]
                print('Registration date:', regDate)

            try:
                cursor.execute(updateProjectQuery,
                                (regDate,
                                 datetime.datetime.now(),
                                 currentProject,
                                 datasource_id))
                db.commit()
            except pymysql.Error as err:
                print(err)
                db.rollback()
        except urllib.error.URLError as e:
            print(e.reason)
except pymysql.Error as err:
    print(err)
