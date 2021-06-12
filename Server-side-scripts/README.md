## Custom omero server-side-scripts

1. Duplicate_Across_Groups.py

The script is intended to be placed into directory $OMERODIR/lib/scripts/omero/util_scripts and can be used to duplicate data within Omero without copying the underlying data. 
It is providing a hard-linking functionality to the Omero.web users, since the omero-cli-duplicate command is only available on command line so far.

In the CAi @HHU it is mainly used to share data between different groups. Annotations are also duplicated but are maintained independently. A quick guide how to use it, can be found at https://wiki.hhu.de/display/CAi/OMERO+data+sharing 

Package omero-cli-duplicate is required for this server-side-script to work, installation via pip is recommended (see https://github.com/ome/omero-cli-duplicate). The main script has been provided by Josh Moore (https://github.com/joshmoore, OME team) and adapted by Anna Hamacher for the CAi needs. Increasing the timeout value might be needed if really large and/or multiple datasets are copied.
