#!/usr/bin/env python
#
# scm-changebar.py
#
# Copyright (c) Olivier Huber <oli.huber@gmail.com> 2012
#
# This was inspired by http://www.matthew.ath.cx/projects/git-changebar
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation version 2.  This program is distributed in the hope that it will
# be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the GNU
# General Public License along with this program; if not, write to the Free
# Software Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307,
# USA.

import sys
import re
import subprocess


#def checkRCS():
#    return


def parseTex(filename):
    tmpDict = {}
    beginList = []
    endList = []
    envList = []
    try:
        f = open(filename)
    except:
        print("the file you provided cannot be opened")
        exit(1)
    patBegin = re.compile(r"\\begin\{([a-z0-9A-Z_*]+)\}")
    patEnd = re.compile(r"\\end\{([a-z0-9A-Z_*]+)\}")
    lineNumber = 1
    for l in f.readlines():
#        print l
        mb = patBegin.search(l)
        me = patEnd.search(l)
        if mb:
#            print mb.group(0)
#            for i in range(1, len(mb.groups()))
            env = mb.group(1) + 'b'
            if env not in tmpDict.keys():
                tmpDict[env] = [lineNumber]
            else:
                # now things are more complex, we have a nested struct
                tmpDict[env].insert(0, lineNumber)
            beginList.append(lineNumber)
            endList.append(0)
            envList.append(mb.group(1))
        elif me:
#            print me.group(0)
            env = me.group(1) + 'b'
            if env not in tmpDict.keys():
                print("error: " + me.group(0) + " found, but no begin !")
                print("line: " + str(lineNumber))
                exit(1)
            else:
                beginLine = tmpDict[env][0]
                indx = beginList.index(beginLine)
                endList[indx] = lineNumber
                del tmpDict[env][0]

        lineNumber = lineNumber + 1
    f.close()
    return (beginList, endList, envList)


def putChangebar(filename, argv, listL):
    filenameOutput = re.sub(r'\.tex$', '.diff.tex', filename)
    f = open(filename)
    output = open(filenameOutput, 'w')
    gitDiff = subprocess.Popen(['git', '--no-pager', 'diff', '--no-color'] +
            argv + ['--', filename], stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
    diff = gitDiff.stdout
    allLines = f.readlines()
    for l in diff.readlines():
        changes = re.match(r"^@@ -[0-9,]* \+([0-9,]*) @@", l)
        if changes:
            [start, length] = changes.group(1).split(',')
            # changes in diff have 3 lines of context before and after
            start = int(start) + 3
            end = start+int(length)-6
            tmpL1 = [i for i in listL if i[0] <= start and i[1] >= start]
            tmpL2 = [i for i in listL if i[0] <= end and i[1] >= end]
            if tmpL1:
                lStart = min(tmpL1, key=lambda x: x[0])[0]-1
            else:
                lStart = start-1
            if tmpL2:
                lEnd = max(tmpL2, key=lambda x: x[1])[1]
            else:
                lEnd = end

            allLines[lStart] = '\cbstart{} ' + allLines[lStart]
            allLines[lEnd] = '\cbend{} ' + allLines[lEnd]

    output.writelines(allLines)
    f.close()
    output.close()
    return gitDiff

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("You have to provide a file name and either a hash (git), \
                revision number (svn) or another file")
        exit(1)
    (bL, eL, envL) = parseTex(sys.argv[1])
    listEnvLines = zip(bL, eL, envL)
    putChangebar(sys.argv[1], sys.argv[2:], listEnvLines)
