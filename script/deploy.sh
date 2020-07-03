#!/bin/bash

# verify that the required Cloud Foundry variables are set
invocation_error=0

# - BXIAM: IBM Cloud API key
if [ -z ${APIKEY+x} ]; then echo 'Error: Environment variable BXIAM is undefined.'; invocation_error=1; fi

# login and set target
./Bluemix_CLI/bin/ibmcloud config --check-version false
./Bluemix_CLI/bin/ibmcloud login --apikey $APIKEY
./Bluemix_CLI/bin/ibmcloud target --cf
./Bluemix_CLI/bin/ibmcloud plugin install cloud-functions -r Bluemix
./Bluemix_CLI/bin/ibmcloud fn action update smdg_code_lookup --kind python-jessie:3 ./endpoint/main.py