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
import datetime
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

datasource_id = sys.argv[1]
password      = sys.argv[2]

adminList = []


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
selectIndexQuery = 'SELECT proj_unixname, indexhtml FROM ow_project_indexes \
                  WHERE datasource_id=%s ORDER BY 1'  # LIMIT 1'

selectQuery = 'SELECT proj_id_num FROM ow_projects \
                WHERE proj_unixname = %s AND datasource_id = %s'

updateDeveloperProjectQuery = 'UPDATE ow_developer_projects  \
                     SET  \
                     dev_loginname = %s, \
                     is_admin = %s, \
                     position = %s, \
                     date_collected = now() \
                     WHERE proj_unixname = %s \
                     AND datasource_id = %s \
                     AND dev_loginname = %s'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

try:
    cursor.execute(selectIndexQuery, (datasource_id))
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        currentProject = project[0]
        html = project[1]
        print('working on', currentProject)

        try:
            regex1 = 'href=\"/users/(.*?)/\">'

            soup = BeautifulSoup(html, "html.parser")
            tr = soup.find_all('tr', align='left')
            for t in tr:
                admin = re.findall(regex1, str(t))
                if admin:
                    for a in admin:
                        adminList.append(a)

        except pymysql.Error as err:
            print(err.reason)
        try:
            cursor.execute(selectQuery, (currentProject, datasource_id))
            projId = cursor.fetchall()

            for ids in projId:
                num = ids[0]
                memberLink = 'https://forge.ow2.org/project/memberlist.php?group_id=' + str(num)

                req = urllib2.Request(memberLink, headers=hdr)
                memberhtml = urllib2.urlopen(req).read()

                soup2 = BeautifulSoup(memberhtml, 'html.parser')
                p = soup2.find_all('p')

                for section in p:
                    table = section.find('table')
                    if table:
                        tr1 = table.find_all('tr')
                        for t in tr1:
                            if len(t) == 9:
                                td = t.find_all('td')
                                for line in td:
                                    regexLogin = '/users/(.*?)/'
                                    login = re.findall(regexLogin, str(line))
                                    if login:
                                        loginname = login[0]
                                        # print(loginname)

                                    regexRole = '<td\salign=\"center\">(.*?)</td>'
                                    role = re.findall(regexRole, str(line))
                                    if role:
                                        if len(role[0]) < 20:
                                            position = role[0]
                                            # print(position)

                                if loginname in adminList:
                                    isadmin = '1'
                                else:
                                    isadmin = '0'
                                # print('isadmin', isadmin)

                                try:
                                    cursor.execute(updateDeveloperProjectQuery,
                                                   (loginname,
                                                    isadmin,
                                                    position,
                                                    currentProject,
                                                    datasource_id,
                                                    loginname))
                                    db.commit()
                                except pymysql.Error as err:
                                    print(err)
                                    db.rollback()

        except urllib2.HTTPError as herror:
            print(herror)
except pymysql.Error as err:
    print(err)
