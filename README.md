**Usage**
For oc
    $ oc version # Get version v3.8.11
    $ python simpletest.py v3.8.11 oc # This command will output cmd and flags in a file named "oc_v3.8.11_cmds.txt"
    Then:
    $ export PATH=/path/to/directory:$PATH # /path/to/directory includes another oc, e.g. v3.7.9
    $ oc version # Get version v3.7.9
    $ python simpletest.py v3.7.9 oc # Similarly
    $ diff -U 1000 oc_v3.7.9_cmds.txt oc_v3.8.11_cmds.txt > diff
    $ grep -e "^[+-]" -e "^ *o" diff | grep -B 1 -e "^[+-]" | grep -v -e "+++" -e "^--" # Will get below output
    ...
    oc get
    +      --include-uninitialized=false
    -      --schema-cache-dir='~/.kube/schema'
    ...


For oadm
  If you installed oadm, just run similar `python simpletest.py v3.8.11 oadm`.  Otherwise, make a fake oadm first:
    $ touch /bin/oadm
    $ chmod a+x /bin/oadm
    $ vi /bin/oadm
    #!/bin/bash
    echo "oadm comes from `which oc` adm"
    oc adm $*

  Then run above `python simpletest.py v3.8.11 oadm` and so on

