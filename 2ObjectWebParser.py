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

# Get list of all projects & urls from the database
selectQuery = 'SELECT proj_unixname, url \
               FROM ow_projects \
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

# set up headers
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

try:
    cursor.execute(selectQuery, (datasource_id))
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        currentProject = project[0]
        projectOWUrl = project[1]
        print('\nworking on', currentProject)

        try:
            # TO-DO: replace this part
            # use the index html that we collected in 1ObjectWebScraper.py
            # then, replace the 'soup' in the lines below
            '''
            projectPage = urllib2.Request(projectOWUrl, headers=hdr)
            myPage = urllib2.urlopen(projectPage).read()
            soup = BeautifulSoup(myPage, "html.parser")
            '''

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

            # Parse out Developer count
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
