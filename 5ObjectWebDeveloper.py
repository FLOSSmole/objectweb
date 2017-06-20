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
# python 5ObjectWebDeveloper.py <datasource_id> <password>
#
# purpose:
# grab information on the users of ObjectWeb
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

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
selectQuery = 'SELECT datasource_id, dev_loginname FROM ow_developer_projects'

updateDevelopersQuery = 'UPDATE ow_developers  \
                     SET \
                     realname = %s, \
                     dev_id = %s, \
                     member_since = %s, \
                     email = %s, \
                     user_url = %s, \
                     user_html = %s, \
                     date_collected = now() \
                     WHERE datasource_id = %s \
                     AND dev_loginname = %s'

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
        datasource_id = project[0]
        loginname = project[1]
        print('working on', loginname)

        try:
            userUrl = 'https://forge.ow2.org/users/' + loginname + '/'
            # print(userUrl)
            req = urllib2.Request(userUrl, headers=hdr)
            userhtml = urllib2.urlopen(req).read()
            html = str(userhtml)
            # print(userhtml)
            soup = BeautifulSoup(userhtml, 'html.parser')

            regexId = 'href=\"/people/viewprofile\.php\?user_id=(.*?)\"'
            userId = re.findall(regexId, str(soup))
            if userId:
                dev_id = userId[0]
                # print(dev_id)

            regexRealName = '<td>Real Name </td>\s*<td><strong>(.*?)</strong></td>'
            realName = re.findall(regexRealName, str(soup))
            if realName:
                name = realName[0]
                # print(name)

            regexEmail = '<td>Your Email Address: </td>\s*<td>\s*<strong><a href=\"(.*?)\">(.*?)</a>'
            emailList = re.findall(regexEmail, str(soup))
            if emailList:
                email = emailList[0]
                for e in email:
                    if 'sendmessage.php' not in e:
                        email = e
                        # print(email)

            regexMemberSince = '<td>\s*Site Member Since	</td>\s*<td><strong>(.*?)</strong>'
            memberSince = re.findall(regexMemberSince, str(soup))
            if memberSince:
                since = memberSince[0]

            try:
                cursor.execute(updateDevelopersQuery, (name,
                                        dev_id,
                                        since,
                                        email,
                                        userUrl,
                                        html,
                                        datasource_id,
                                        loginname))
                db.commit()
                print(loginname + ' updated!')
            except pymysql.Error as err:
                print(err)
                db.rollback()
        except urllib2.HTTPError as herror:
            print(herror)
except pymysql.Error as err:
    print(err)
