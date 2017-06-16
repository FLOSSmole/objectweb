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
# python 3ObjectWebParserContinue.py <datasource_id> <password>
#
# purpose:
# grab project page and parse out interesting bits, write those to db
################################################################

import sys
import pymysql
import re
import datetime
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

projDesc = None

# Update the indexes table
def indexes():
    try:
        cursor.execute(updateIndexesQuery,
                       (projectHtml,
                        datetime.datetime.now(),
                        currentProject,
                        datasource_id))
        db.commit()
        print(currentProject, "updated in indexes table!")
    except pymysql.Error as err:
        print(err)
        db.rollback()


# Update the description table
def description():
    try:
        cursor.execute(updateDescriptionQuery,
                       (projDesc,
                        datetime.datetime.now(),
                        currentProject,
                        datasource_id))
        db.commit()
        print(currentProject, "updated in description table!")
    except pymysql.Error as err:
        print(err)
        db.rollback()


# Update the environment table
def environment():
    try:
        cursor.execute(updateEnvironmentQuery,
                       (code1,
                        descr1,
                        datetime.datetime.now(),
                        currentProject,
                        datasource_id,
                        code1))
        db.commit()
        print(currentProject, "updated in environment table!")
    except pymysql.Error as err:
        print(err)
        db.rollback()


# Update the audience table
def audience():
    try:
        cursor.execute(updateAudienceQuery,
                       (code2,
                        descr2,
                        datetime.datetime.now(),
                        currentProject,
                        datasource_id,
                        code2))
        db.commit()
        print(currentProject, "updated in audience table!")
    except pymysql.Error as err:
        print(err)
        db.rollback()


# Update the licenses table
def licenses():
    try:
        cursor.execute(updateLicensesQuery,
                       (code3,
                        descr3,
                        datetime.datetime.now(),
                        currentProject,
                        datasource_id,
                        code3))
        db.commit()
        print(currentProject, "updated in licenses table!")
    except pymysql.Error as err:
        print(err)
        db.rollback()


# Update the operating system table
def systems():
    try:
        cursor.execute(updateSystemQuery,
                       (code4,
                        descr4,
                        datetime.datetime.now(),
                        currentProject,
                        datasource_id,
                        code4))
        db.commit()
        print(currentProject, "updated in system table!")
    except pymysql.Error as err:
        print(err)
        db.rollback()


# Update the language table
def language():
    try:
        cursor.execute(updateLanguageQuery,
                       (code5,
                        descr5,
                        datetime.datetime.now(),
                        currentProject,
                        datasource_id,
                        code5))
        db.commit()
        print(currentProject, "updated in language table!")
    except pymysql.Error as err:
        print(err)
        db.rollback()


# Update the topic table
def topic():
    try:
        cursor.execute(updateTopicQuery,
                       (code6,
                        descr6,
                        datetime.datetime.now(),
                        currentProject,
                        datasource_id,
                        code6))
        db.commit()
        print(currentProject, "updated in topic table!")
    except pymysql.Error as err:
        print(err)
        db.rollback()


# Update the status table
def status():
    try:
        cursor.execute(updateStatusQuery,
                       (code7,
                        descr7,
                        codeOnPage,
                        datetime.datetime.now(),
                        currentProject,
                        datasource_id,
                        code7))
        db.commit()
        print(currentProject, "updated in status table!")
    except pymysql.Error as err:
        print(err)
        db.rollback()


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
selectQuery = 'SELECT proj_unixname, url, datasource_id FROM ow_projects \
              ORDER BY 1'# LIMIT 1'

updateIndexesQuery = 'UPDATE ow_project_indexes \
                     SET  \
                     indexhtml = %s, \
                     date_collected = %s \
                     WHERE proj_unixname = %s \
                     AND datasource_id = %s;'

updateDescriptionQuery = 'UPDATE ow_project_description \
                         SET \
                         description = %s, \
                         date_collected = %s \
                         WHERE proj_unixname = %s \
                         AND datasource_id = %s;'

updateEnvironmentQuery = 'UPDATE ow_project_environment \
                          SET \
                          code = %s, \
                          description = %s, \
                          date_collected = %s \
                          WHERE proj_unixname = %s \
                          AND datasource_id = %s \
                          AND code = %s;'

updateAudienceQuery = 'UPDATE ow_project_intended_audience \
                          SET \
                          code = %s, \
                          description = %s, \
                          date_collected = %s \
                          WHERE proj_unixname = %s \
                          AND datasource_id = %s \
                          AND code = %s;'

updateLicensesQuery = 'UPDATE ow_project_licenses \
                          SET \
                          code = %s, \
                          description = %s, \
                          date_collected = %s \
                          WHERE proj_unixname = %s \
                          AND datasource_id = %s \
                          AND code = %s;'

updateSystemQuery = 'UPDATE ow_project_operating_system \
                          SET \
                          code = %s, \
                          description = %s, \
                          date_collected = %s \
                          WHERE proj_unixname = %s \
                          AND datasource_id = %s \
                          AND code = %s;'

updateLanguageQuery = 'UPDATE ow_project_programming_language \
                          SET \
                          code = %s, \
                          description = %s, \
                          date_collected = %s \
                          WHERE proj_unixname = %s \
                          AND datasource_id = %s \
                          AND code = %s;'


updateTopicQuery = 'UPDATE ow_project_topic \
                          SET \
                          code = %s, \
                          description = %s, \
                          date_collected = %s \
                          WHERE proj_unixname = %s \
                          AND datasource_id = %s \
                          AND code = %s;'


updateStatusQuery = 'UPDATE ow_project_status \
                          SET \
                          code = %s, \
                          description = %s, \
                          code_on_page = %s, \
                          date_collected = %s \
                          WHERE proj_unixname = %s \
                          AND datasource_id = %s \
                          AND code = %s;'


# set up headers
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

try:
    cursor.execute(selectQuery)
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        currentProject = project[0]
        projectUrl = project[1]
        datasource_id = project[2]
        print('\nworking on', currentProject)

        try:
            projectPage = urllib2.Request(projectUrl, headers=hdr)
            myPage = urllib2.urlopen(projectPage).read()
            soup = BeautifulSoup(myPage, "html.parser")
            projectHtml = str(soup)

            # Get description of project
            descriptionSection = soup.find_all("td", width='99%')

            for desc in descriptionSection:
                descriptionLines = desc.find('p')
                for line in descriptionLines:
                    if line != projDesc:
                        projDesc = line

            details = soup.find_all('li')

            for d in details:
                regex = 'cat=(.*?)\">'

                if 'Status' in d.contents[0]:
                    for stat in d.contents[1:]:
                        match = re.findall(regex, str(stat))
                        if match:
                            code7 = match[0]
                        for s in stat:
                            if len(s) > 1:
                                status1 = s
                                codeOnPage = status1.split(' -')[0]
                                descr7 = status1.split('- ')[1]
                                print(code7, descr7, codeOnPage)
                                status()  # Updates the status table

                if 'Environment' in d.contents[0]:
                    for envi in d.contents[1:]:
                        match = re.findall(regex, str(envi))
                        if match:
                            code1 = match[0]
                        for e in envi:
                            if len(e) > 1:
                                descr1 = e
                                print(code1, descr1)
                                environment()  # Updates the environment table

                if 'Audience' in d.contents[0]:
                    for aud in d.contents[1:]:
                        match = re.findall(regex, str(aud))
                        if match:
                            code2 = match[0]
                        for a in aud:
                            if len(a) > 1:
                                descr2 = a
                                print(code2, descr2)
                                audience()  # Updates the audience table

                if 'License' in d.contents[0]:
                    for lic in d.contents[1:]:
                        match = re.findall(regex, str(lic))
                        if match:
                            code3 = match[0]
                        for l in lic:
                            if len(l) > 1:
                                descr3 = l
                                print(code3, descr3)
                                licenses()  # Updates the licenses table

                if 'System' in d.contents[0]:
                    for sys in d.contents[1:]:
                        match = re.findall(regex, str(sys))
                        if match:
                            code4 = match[0]
                        for s in sys:
                            if len(s) > 1:
                                descr4 = s
                                print(code4, descr4)
                                systems()  # Updates systems table

                if 'Language' in d.contents[0]:
                    for lang in d.contents[1:]:
                        match = re.findall(regex, str(lang))
                        if match:
                            code5 = match[0]
                        for lan in lang:
                            if len(lan) > 1:
                                descr5 = lan
                                print(code5, descr5)
                                language()  # Updates languages table

                if 'Topic' in d.contents[0]:
                    for top in d.contents[1:]:
                        match = re.findall(regex, str(top))
                        if match:
                            code6 = match[0]
                        for t in top:
                            if len(t) > 1:
                                descr6 = t
                                print(code6, descr6)
                                topic()  # Updates topic table

            indexes()  # Updates the indexes table
            description()  # Updates the description table

        except pymysql.Error as err:
            print(e.reason)
except pymysql.Error as err:
    print(err)
