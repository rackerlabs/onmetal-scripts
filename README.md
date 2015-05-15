onmetal-scripts
===============

Scripts to help operate Rackspace OnMetal. These scripts are being
provided to the community as a reference and starting point. Many are specific
to the configuration and environment that Rackspace OnMetal uses.

Note: these are not being actively developed or maintained at this point.


Usage Instructions
------------------
```
git clone git@github.com:rackerlabs/onmetal-scripts
cd onmetal-scripts
tox -evenv
source .tox/venv/bin/activate
source /path/to/ironic/credentials/file
python ironic_scripts/something.py
```
