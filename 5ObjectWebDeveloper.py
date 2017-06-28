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

datasource_id = sys.argv[1]
dbpasswd      = sys.argv[2]
dbhost = 'flossdata.syr.edu'
dbuser = 'megan'
dbschema = 'objectweb'

# establish database connection: SYR
try:
    dbconn = pymysql.connect(host=dbhost,
                             user=dbuser,
                             passwd=dbpasswd,
                             db=dbschema,
                             use_unicode=True,
                             charset='utf8mb4')
    cursor = dbconn.cursor()
except pymysql.Error as err:
    print(err)

# Get list of all developers that we spotted on any actual project
selectQuery = 'SELECT dev_loginname \
               FROM ow_developer_projects\
               WHERE datasource_id = %s'

insertDevelopersQuery = 'INSERT INTO ow_developers \
                        (dev_loginname, \
                        realname, \
                        dev_id, \
                        datasource_id, \
                        member_since, \
                        email, \
                        user_url, \
                        user_html, \
                        date_collected) \
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, now())'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

try:
    cursor.execute(selectQuery, (datasource_id,))
    listOfPeople = cursor.fetchall()

    for project in listOfPeople:
        print('***person:')
        dev_loginname = project[0]
        print('working on', dev_loginname)
        realname = ''
        since = ''
        email = ''
        userUrl = ''
        userhtml = ''

        try:
            userUrl = 'https://forge.ow2.org/users/' + dev_loginname
            print("userUrl:", userUrl)

            req = urllib2.Request(userUrl, headers=hdr)
            userhtml = urllib2.urlopen(req).read()
            soup = BeautifulSoup(userhtml, 'html.parser')
         
            # get the developer's number
            regexId = 'href=\"/people/viewprofile\.php\?user_id=(.*?)\"'
            userNum = re.findall(regexId, str(soup))
            if userNum:
                devId = userNum[0]
                print("num:", devId)

            # get the developer's real name
            regexRealName = '<td>Real Name </td>\s*<td><strong>(.*?)</strong></td>'
            realName = re.findall(regexRealName, str(soup))
            if realName:
                realname = realName[0]
                print("name:", realname)

            # get developer's email address
            regexEmail = '<td>Your Email Address: </td>\s*<td>\s*<strong><a href=\"(.*?)\">(.*?)</a>'
            emailList = re.findall(regexEmail, str(soup))
            if emailList:
                email = emailList[0]
                for e in email:
                    if 'sendmessage.php' not in e:
                        email = e
                        print("email:", email)

            # get member since
            regexMemberSince = '<td>\s*Site Member Since	</td>\s*<td><strong>(.*?)</strong>'
            memberSince = re.findall(regexMemberSince, str(soup))
            if memberSince:
                since = memberSince[0]
                print("since:", since)

            try:
                cursor.execute(insertDevelopersQuery, (dev_loginname,
                                                       realname,
                                                       devId,
                                                       datasource_id,
                                                       since,
                                                       email,
                                                       userUrl,
                                                       userhtml))
                dbconn.commit()
            except pymysql.Error as err:
                print(err)
                dbconn.rollback()
        except urllib2.HTTPError as herror:
            print(herror)
except pymysql.Error as err:
    print(err)

dbconn.close()
