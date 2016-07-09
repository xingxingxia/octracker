[PRE ACTION]

  Before very first time: install python and 3rd party lib (subprocess, xlwt, xlrd, xlutils)

  To check updates - Before each single run: `git add oc_log` and `git add oadm_log`, they are no used only for track and compare log

[EXEC examples & OUTPUT]


        $ python simpletest.py vxxx oc (or "oadm")

  output 2 files:

  1) octracker.xls - a history file for all details

  2) oc_log - latest commands


        $ python simpletest.py vxxx2 diff

  output 3 files:

  1) same as above

  2) same as above

  3) diff file (oc_difflog_vx.x.x) will output the diff by "git diff" between this version of "oc_log" and lastest version of "oc_log".

*[NOTE]

  1) first param "vxxx" is an example, it could be any name.

  2) to explain why need git add before each run, below metion about "1st/2nd/3rd time" is an example

  If use "diff", before the 2nd time to run the script, need to do git add first. Otherwise, the 3rd log will only compare with the 1st one.

  If do git add just after the 1st time, it's not a big problem, BUT manullay do git diff again will not show any different again, this is not good for manual check git diff.

