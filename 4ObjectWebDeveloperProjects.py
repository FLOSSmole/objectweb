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
# python 4ObjectWebDeveloperProjects.py <datasource_id> <password>
#
# purpose:
# grab project page and parse out information on the developers in each project
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

datasource_id = sys.argv[1]
dbpasswd      = sys.argv[2]
dbhost = ''
dbuser = ''
dbschema = ''

# establish database connection: SYR
try:
    db = pymysql.connect(host=dbhost,
                     user=dbuser,
                     passwd=dbpasswd,
                     db=dbschema,
                     use_unicode=True,
                     charset='utf8mb4')
    cursor = db.cursor()
except pymysql.Error as err:
    print(err)

# Get list of all projects & urls & project numbers from the database
selectIndexQuery = 'SELECT opi.proj_unixname, opi.indexhtml, op.proj_id_num \
                    FROM ow_project_indexes opi \
                    INNER JOIN ow_projects op \
                    ON opi.datasource_id = op.datasource_id \
                    AND opi.proj_unixname = op.proj_unixname \
                    WHERE opi.datasource_id = %s \
                    AND op.datasource_id = %s \
                    ORDER BY 1'

updateDeveloperProjectHtml = 'UPDATE ow_project_indexes \
                              SET devhtml = %s \
                              WHERE proj_unixname = %s \
                              AND datasource_id = %s'

insertDeveloperProjectQuery = 'INSERT INTO ow_developer_projects \
                               (dev_loginname, \
                                is_admin, \
                                position, \
                                date_collected, \
                                datasource_id, \
                                proj_unixname) \
                               VALUES(%s, %s, %s, now(), %s, %s)'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

devPagePrefix = 'https://forge.ow2.org/project/memberlist.php?group_id='
try:
    cursor.execute(selectIndexQuery, (datasource_id, datasource_id))
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        adminList = []
        currentProject = project[0]
        html = project[1]
        projId = project[2]
        print('working on', currentProject, "(", projId, ")")

        try:
            memberLink = devPagePrefix + str(projId)
    
            req = urllib2.Request(memberLink, headers=hdr)
            memberHtml = urllib2.urlopen(req).read()
            
            if memberHtml:
                # update the database table with this new developers html
                try:
                    cursor.execute(updateDeveloperProjectHtml, (memberHtml, 
                                                                currentProject,
                                                                datasource_id))
                except pymysql.Error as err:
                    print(err)
                    
                soup2 = BeautifulSoup(memberHtml, 'html.parser')
                p = soup2.find_all('p')
        
                for section in p:
                    table = section.find('table')
                    if table:
                        everyone = table.find_all('tr')
                        for person in everyone:
                            print("***FOUND PERSON***")
                            devlogin = ''
                            isadmin = '0'
                            position = ''
                            if len(person) == 9:
                                # find the users
                                people = person.find_all('td')
                                for item in people:
                                    # grab their system username
                                    regexLogin = '/users/(.*?)/'
                                    login = re.findall(regexLogin, str(item))
                                    if login:
                                        devlogin = login[0]
                                        print('--name:', devlogin)
    
                                    # find that user's role on the project
                                    regexRole = '<td\salign=\"center\">(.*?)</td>'
                                    role = re.findall(regexRole, str(item))
                                    if role:
                                        if len(role[0]) < 20:
                                            position = role[0]
                                            print("--position:", position)

                                    # find whether they are an admin
                                    # <td><strong>Andrea Zoppello</strong>
                                    regexAdmin = '<td><strong>(.*?)'
                                    admin = re.findall(regexAdmin, str(item))
                                    if admin:
                                        isadmin = '1'
                                        print('--isadmin:', isadmin)
                                try:
                                    cursor.execute(insertDeveloperProjectQuery,
                                                   (devlogin,
                                                    isadmin,
                                                    position,
                                                    datasource_id,
                                                    currentProject))
                                    db.commit()
                                except pymysql.Error as err:
                                    print(err)
                                    db.rollback()


        except urllib2.HTTPError as herror:
            print(herror)
except pymysql.Error as err:
    print(err)
db.close()
