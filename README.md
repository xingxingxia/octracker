This is forked from [xiaocwan/octracker](https://github.com/xiaocwan/octracker) with some refining.

**Usage**

    python simpletest.py [/path/to/]oc [adm]

    Given oc version v3.8.11
    $ python simpletest.py oc
    Will create oc_v3.8.11_cmds.txt including oc sub cmds and flags

    $ python simpletest.py oc adm
    Will create oc_adm_v3.8.11_cmds.txt including oc adm sub cmds and flags in file oc_adm_v3.8.11_cmds.txt

    Compare between 2 versions:
    $ diff --ignore-blank-lines -U 1000 oc_v3.7.9_cmds.txt oc_v3.8.11_cmds.txt > diff
    $ grep -e "^[+-]" -e "^ *o" diff | grep -B 1 -e "^[+-]" | grep -v -e "+++" -e "^--"
    Will get output:
    ...
    oc get
    +      --include-uninitialized=false
    ...

