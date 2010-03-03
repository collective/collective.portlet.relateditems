collective.portlet.relateditems
=================================

Overview
--------

This is a simple portlet that displays content similar to the present context.
Related items are compiled based on the context title and keywords. 
In case of a folderish context related items are computed based on the contents of the folder and the folder information.

Status
------

The relateditems portlet is used in production. See http://www.v2.nl

Options
-------

The portlet has the following options available to it on the Add screen.

count
    This is the number of recent items that will be shown in the portlet.

states
    The workflow states the items must be in to be shown in the portlet.

allowed_types
    The allowed types to be shown in the portlet and the 'more...' link search

show_all_types
    Choose whether or not all types should be available for the 'more...' link.  This will search for all content types when clicking on 'more...'
