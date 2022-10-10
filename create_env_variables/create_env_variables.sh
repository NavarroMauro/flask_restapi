#!/bin/sh

# Locate the directory for the conda environment in your terminal window by running in the terminal echo $CONDA_PREFIX.
# Enter that directory and create these subdirectories and files:
cd $CONDA_PREFIX
mkdir -p ./etc/conda/activate.d
mkdir -p ./etc/conda/deactivate.d
touch ./etc/conda/activate.d/env_vars.sh
touch ./etc/conda/deactivate.d/env_vars.sh

cat <<EOF >./etc/conda/activate.d/env_vars.sh
# here you can add any commands you want to run when the environment is activated
first line
second line
third line
EOF

cat <<EOF >./etc/conda/deactivate.d/env_vars.sh
# here you can add any commands you want to run when the environment is deactivated
first line
second line
third line
EOF
