#!/bin/bash

# get current path
this_file=$(realpath $0)
PYTHONPATH=$(dirname $this_file)

# create necessary directory for ol tool to function
[ ! -d "~/.0L" ] && mkdir -p ~/.0L

# copy the ol tool config file, if it exists, only
# overwrite destination file when the source file 
# is newer.
cp -u $PYTHONPATH/assets/0L.toml ~/.0L

# make the ol tool executable
chmod +x $PYTHONPATH/bin/ol
chmod +x $PYTHONPATH/bin/txs
chmod +x $PYTHONPATH/bin/onboard

# add the path of the ol tool to the PATH variable. 
# This should be done every time you logout and login
# again. To prevent this, you can add this line at
# the bottom of the .bashrc file in your home dir.
export PATH="$PYTHONPATH/bin:$PATH"

# To restore db:
# gunzip < ./db/dump_all.gz | docker exec -i adhoc-db psql -U ol_intel -d viz_dev
