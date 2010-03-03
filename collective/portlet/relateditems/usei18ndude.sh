#!/bin/bash 

# start with ./use18ndude.sh 

PRODUCT="collective.portlet.relateditems"

# if you want to add ne language, replace <LANGUAGE_CODE> with language code
# and run these two commands: 
# mkdir -p locales/<LANGUAGE_CODE>/LC_MESSAGES/
# touch locales/<LANGUAGE_CODE>/LC_MESSAGES/$PRODUCT.po 

i18ndude rebuild-pot --pot locales/$PRODUCT.pot --create $PRODUCT  ./
i18ndude sync --pot locales/$PRODUCT.pot locales/*/LC_MESSAGES/$PRODUCT.po 

