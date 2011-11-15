#!/bin/bash 

# start with ./use18ndude.sh 

PRODUCT="collective.portlet.relateditems"

# if you want to add a new language, replace <LANGUAGE_CODE> with language code
# and run these two commands: 
#
# mkdir -p locales/<LANGUAGE_CODE>/LC_MESSAGES/
# touch locales/<LANGUAGE_CODE>/LC_MESSAGES/$PRODUCT.po 
#
# Similar for the plone domain:
#
# mkdir -p plonelocales/<LANGUAGE_CODE>/LC_MESSAGES/
# touch plonelocales/<LANGUAGE_CODE>/LC_MESSAGES/plone.po 
# touch i18n/${PRODUCT}-plone-<LANGUAGE_CODE>.po

i18ndude rebuild-pot --pot locales/$PRODUCT.pot --create $PRODUCT  ./
i18ndude sync --pot locales/$PRODUCT.pot locales/*/LC_MESSAGES/$PRODUCT.po 

# Translations for the plone domain are in both i18n (Plone 3) and
# plonelocales (Plone 4).  The pot file is created and updated manually.
i18ndude sync --pot plonelocales/plone.pot plonelocales/*/LC_MESSAGES/plone.po i18n/${PRODUCT}-plone-*.po

# Optionally copy the plone translations from plonelocales to i18n or
# the other way around.  Let's not do this by default, as it will be
# unexpected.
for dir in plonelocales/*/; do
    lang=$(echo $dir | cut -d "/" -f2)
    ## plonelocales is canonical, copy to i18n:
    #cp plonelocales/$lang/LC_MESSAGES/plone.po i18n/${PRODUCT}-plone-${lang}.po
    ## i18n is canonical, copy to plonelocales:
    #cp i18n/${PRODUCT}-plone-${lang}.po plonelocales/$lang/LC_MESSAGES/plone.po
done
