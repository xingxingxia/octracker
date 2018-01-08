**Usage**


    $ python simpletest.py oc
    Given oc version is v3.8.11, this command will output the cmd and flags in file like oc_v3.8.11_cmds.txt
    $ python simpletest.py oc adm
    This command will output the `oc adm` cmd and flags in file like oc_adm_v3.8.11_cmds.txt

    If you want to check oc of another version, e.g. v3.7.9, run:
    $ export PATH=/path/to/directory:$PATH # /path/to/directory is the directory containing oc of another version
    $ python simpletest.py oc
    $ python simpletest.py oc adm

    Then run:
    $ diff --ignore-blank-lines -U 1000 oc_v3.7.9_cmds.txt oc_v3.8.11_cmds.txt > diff
    $ grep -e "^[+-]" -e "^ *o" diff | grep -B 1 -e "^[+-]" | grep -v -e "+++" -e "^--"
    This will get below output:
    ...
    oc get
    +      --include-uninitialized=false
    ...

