#!/usr/bin/env python3
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
# python 3ObjectWebParser.py <datasource_id> <password>
#
# purpose:
# grab project page and parse out interesting bits, write those to db
################################################################

import pymysql
import re
import sys
from bs4 import BeautifulSoup

datasourceID = sys.argv[1]
dbuser = 'megan'
dbpw = sys.argv[2]
dbschema = 'objectweb'
dbhost = 'flossdata.syr.edu'

projDesc = None

# Update the description table
def updateDescription():
    try:
        cursor.execute(insertDescriptionQuery,
                       (currentProject,
                        projDesc,
                        datasourceID))
        dbconn.commit()
        print(currentProject, "inserted description!")
    except pymysql.Error as err:
        print(err)
        dbconn.rollback()

# update a given table using the query & table passed
def runQuery(word, query):
    code = None
    descr = None
    for d in details:
        regex = 'cat=(.*?)\">'

        if word in d.contents[0]:
            for line in d.contents[1:]:
                match = re.findall(regex, str(line))
                if match:
                    code = match[0]
                for l in line:
                    if len(l) > 1:
                        descript = l
                        if word == 'Status':
                            codeOnPage = descript.split(' -')[0]
                            descr = descript.split('- ')[1]
                            print(code, descr, codeOnPage)
                            
                            try:    
                                cursor.execute(insertStatusQuery,
                                               (currentProject,
                                                code,
                                                descr,
                                                codeOnPage,
                                                datasourceID))
                                dbconn.commit()
                                print(currentProject, "inserted status!")
                            except pymysql.Error as err:
                                print(err)
                                dbconn.rollback()
                        else:
                            try:
                                print(code, descript)
                                cursor.execute(query,
                                               (currentProject,
                                                datasourceID,
                                                code,
                                                descript))
                                dbconn.commit()
                                print(currentProject, "inserted", word, "!")
                            except pymysql.Error as err:
                                print(err)
                                dbconn.rollback()

try:
    dbconn = pymysql.connect(host=dbhost,
                             user=dbuser,
                             passwd=dbpw,
                             db=dbschema,
                             use_unicode=True,
                             charset='utf8mb4')
    cursor = dbconn.cursor()
except pymysql.Error as err:
    print(err)

# Get list of all projects & urls from the database
selectQuery = 'SELECT proj_unixname, indexhtml \
               FROM ow_project_indexes \
               WHERE datasource_id= %s \
               ORDER BY 1'

insertDescriptionQuery = 'INSERT INTO ow_project_description \
                         (proj_unixname, \
                         description, \
                         datasource_id, \
                         date_collected) \
                         VALUES(%s, %s, %s, now())'

insertEnvironmentQuery = 'INSERT INTO ow_project_environment \
                          (proj_unixname, \
                          datasource_id, \
                          code, \
                          description, \
                          date_collected) \
                          VALUES (%s, %s, %s, %s, now())'

insertAudienceQuery = 'INSERT INTO ow_project_intended_audience \
                          (proj_unixname, \
                          datasource_id, \
                          code, \
                          description, \
                          date_collected) \
                          VALUES (%s, %s, %s, %s, now())'

insertLicensesQuery = 'INSERT INTO ow_project_licenses \
                          (proj_unixname, \
                          datasource_id, \
                          code, \
                          description, \
                          date_collected) \
                          VALUES (%s, %s, %s, %s, now())'

insertSystemQuery = 'INSERT INTO ow_project_operating_system \
                          (proj_unixname, \
                          datasource_id, \
                          code, \
                          description, \
                          date_collected) \
                          VALUES (%s, %s, %s, %s, now())'

insertLanguageQuery = 'INSERT INTO ow_project_programming_language \
                          (proj_unixname, \
                          datasource_id, \
                          code, \
                          description, \
                          date_collected) \
                          VALUES (%s, %s, %s, %s, now())'


insertTopicQuery = 'INSERT INTO ow_project_topic \
                          (proj_unixname, \
                          datasource_id, \
                          code, \
                          description, \
                          date_collected) \
                          VALUES (%s, %s, %s, %s, now())'


insertStatusQuery = 'INSERT INTO ow_project_status \
                          (proj_unixname, \
                          code, \
                          description, \
                          code_on_page, \
                          date_collected, \
                          datasource_id) \
                          VALUES (%s, %s, %s, %s, now(), %s)'

try:
    cursor.execute(selectQuery, (datasourceID,))
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        currentProject = project[0]
        html = project[1]
        print('\nworking on', currentProject)

        try:
            soup = BeautifulSoup(html, 'html.parser')
            projectHtml = str(soup)

            # Get description of project
            descriptionSection = soup.find_all('td', width='99%')

            for desc in descriptionSection:
                descriptionLines = desc.find('p')
                for line in descriptionLines:
                    if line != projDesc:
                        projDesc = line

            details = soup.find_all('li')

            runQuery('Status', insertStatusQuery)  # Updates the status table
            runQuery('Environment', insertEnvironmentQuery)  # Updates the environment table
            runQuery('Audience', insertAudienceQuery)  # Updates the intended audience table
            runQuery('License', insertLicensesQuery)  # Updates the licenses table
            runQuery('System', insertSystemQuery)  # Updates the operating system table
            runQuery('Language', insertLanguageQuery)  # Updates the programming language table
            runQuery('Topic', insertTopicQuery)  # Updates the topic table

            updateDescription()  # Updates the description table

        except pymysql.Error as err:
            print(err.reason)
except pymysql.Error as err:
    print(err)

dbconn.close()
