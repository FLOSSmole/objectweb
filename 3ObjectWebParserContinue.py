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

import pymysql
import re
import datetime
from bs4 import BeautifulSoup

projDesc = None
code = None
descr = None

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


def run(word, query):
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
                                cursor.execute(updateStatusQuery,
                                               (code,
                                                descr,
                                                codeOnPage,
                                                datetime.datetime.now(),
                                                currentProject,
                                                datasource_id,
                                                code))
                                db.commit()
                                print(currentProject, "updated in status table!")
                            except pymysql.Error as err:
                                print(err)
                                db.rollback()
                        else:
                            try:
                                print(code, descript)
                                cursor.execute(query,
                                               (code,
                                                descript,
                                                datetime.datetime.now(),
                                                currentProject,
                                                datasource_id,
                                                code))
                                db.commit()
                                print(currentProject, "updated in", word, "table!")
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
selectQuery = 'SELECT proj_unixname, indexhtml, datasource_id FROM ow_project_indexes \
              ORDER BY 1'

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

try:
    cursor.execute(selectQuery)
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        currentProject = project[0]
        html = project[1]
        datasource_id = project[2]
        print('\nworking on', currentProject)

        try:
            soup = BeautifulSoup(html, "html.parser")
            projectHtml = str(soup)

            # Get description of project
            descriptionSection = soup.find_all("td", width='99%')

            for desc in descriptionSection:
                descriptionLines = desc.find('p')
                for line in descriptionLines:
                    if line != projDesc:
                        projDesc = line

            details = soup.find_all('li')

            run('Status', updateStatusQuery)  # Updates the status table
            run('Environment', updateEnvironmentQuery)  # Updates the environment table
            run('Audience', updateAudienceQuery)  # Updates the intended audience table
            run('License', updateLicensesQuery)  # Updates the licenses table
            run('System', updateSystemQuery)  # Updates the operating system table
            run('Language', updateLanguageQuery)  # Updates the programming language table
            run('Topic', updateTopicQuery)  # Updates the topic table

            description()  # Updates the description table

        except pymysql.Error as err:
            print(err.reason)
except pymysql.Error as err:
    print(err)
