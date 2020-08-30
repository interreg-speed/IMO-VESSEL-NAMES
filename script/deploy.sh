#!/bin/bash

# verify that the required Cloud Foundry variables are set
invocation_error=0

# - BXIAM: IBM Cloud API key
if [ -z ${APIKEY+x} ]; then echo 'Error: Environment variable BXIAM is undefined.'; invocation_error=1; fi
# set optional Cloud Foundry variables if they are not set
# - CF_API: IBM Cloud API endpoint (default to US-South region)
if [ -z ${CF_API+x} ]; then export CF_API='https://api.ng.bluemix.net'; fi

if [ ${invocation_error} -eq 1 ]; then echo 'Something went wrong, check for previous errors.'; exit 1; fi

# login and set target
ls -la

ibmcloud config --check-version false
ibmcloud login -a $CF_API --apikey $APIKEY
ibmcloud target -o $CF_ORG -s $CF_SPACE
ibmcloud plugin install cloud-functions -r Bluemix
ibmcloud fn action update imo_vessel_names --kind python-jessie:3 ./endpoint/main.py