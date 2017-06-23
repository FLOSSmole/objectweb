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
# python 2ObjectWebParser.py <datasource_id> <password>
#
# purpose:
# grab project page and parse out interesting bits, write those to db
################################################################
import sys
import pymysql
import re
from bs4 import BeautifulSoup

datasource_id = sys.argv[1]
dbpw = sys.argv[2]
dbhost = 'flossdata.syr.edu'
dbuser = 'megan'
dbschema = 'objectweb'

homePageUrl = None
regDate = None
groupId = None
devCount = None

# establish database connection: SYR
try:
    dbconn = pymysql.connect(host=dbhost,
                             user=dbuser,
                             passwd=dbpw,
                             db=dbschema,
                             use_unicode=True,
                             charset="utf8mb4")
    cursor = dbconn.cursor()
except pymysql.Error as err:
    print(err)

# Get list of all projects & indexes from the database
# (Objectweb is small enough that we can get all these at once)
selectQuery = 'SELECT proj_unixname, indexhtml \
               FROM ow_project_indexes \
               WHERE datasource_id=%s \
               ORDER BY 1'

updateProjectQuery = 'UPDATE ow_projects \
                      SET \
                      real_url = %s, \
                      date_registered = %s, \
                      proj_id_num =%s, \
                      dev_count = %s, \
                      date_collected = now() \
                      WHERE proj_unixname = %s \
                      AND datasource_id = %s'

try:
    cursor.execute(selectQuery, (datasource_id))
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        currentProject = project[0]
        html = project[1]
        print('\nworking on', currentProject)

        try:
            soup = BeautifulSoup(html, "html.parser")

            # Parse out homepage
            regex1 = '<a href="(.*?)"><img alt="Home Page"'
            match1 = re.findall(regex1, str(soup))[0]

            if match1:
                homePageUrl = match1
                print("--homepage:", homePageUrl)

            # Parse out registration date
            regex2 = 'Registered:(.*?)\d(.*?)\s*<'
            match2 = re.findall(regex2, str(soup))[0]

            if match2:
                for m in match2:
                    if len(m) > 5:
                        regDate = '2' + m
                        print('--registration date:', regDate)

            # Parse out group id
            regex3 = '<input name=\"group_id\" type=\"hidden\" value=\"(.*?)\"/>'
            match3 = re.findall(regex3, str(soup))[0]

            if match3:
                groupId = match3
                print("--group id: ", groupId)

            # Parse out developer count
            regex4 = 'class=\"develtitle\">Developers:</span><br/>\s*(.*?)\s*<a'
            match4 = re.findall(regex4, str(soup))[0]

            if match4:
                devCount = match4
                print("--dev count: ", devCount)

            try:
                cursor.execute(updateProjectQuery,
                               (homePageUrl,
                                regDate,
                                groupId,
                                devCount,
                                currentProject,
                                datasource_id))
                dbconn.commit()
            except pymysql.Error as err:
                print(err)
                dbconn.rollback()
        except pymysql.Error as err:
            print(err.reason)
except pymysql.Error as err:
    print(err)

dbconn.close()
