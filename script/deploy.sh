#!/bin/bash

# verify that the required Cloud Foundry variables are set
invocation_error=0

# - BXIAM: IBM Cloud API key
if [ -z ${APIKEY+x} ]; then echo 'Error: Environment variable BXIAM is undefined.'; invocation_error=1; fi
# - CF_ORGANIZATION: IBM Cloud/Cloud Foundry organization name
if [ -z ${CF_ORGANIZATION+x} ]; then echo 'Error: Environment variable CF_ORGANIZATION is undefined.'; invocation_error=1; fi
# - CF_SPACE: IBM Cloud/Cloud Foundry space name
if [ -z ${CF_SPACE+x} ]; then echo 'Error: Environment variable CF_SPACE is undefined.'; invocation_error=1; fi

# set optional Cloud Foundry variables if they are not set
# - CF_API: IBM Cloud API endpoint (default to US-South region)
if [ -z ${CF_API+x} ]; then export CF_API='https://cloud.ibm.com'; fi

if [ ${invocation_error} -eq 1 ]; then echo 'Something went wrong, check for previous errors.'; exit 1; fi

# login and set target
./Bluemix_CLI/bin/ibmcloud config --check-version false
./Bluemix_CLI/bin/ibmcloud login --apikey $APIKEY
./Bluemix_CLI/bin/ibmcloud target --cf
./Bluemix_CLI/bin/ibmcloud plugin install cloud-functions -r Bluemix
./Bluemix_CLI/bin/ibmcloud fn action update smdg_code_lookup --kind python-jessie:3 ./endpoint/main.py