from ZTUtils import make_query

import time
from zope.interface import implements
from Products.ATContentTypes.interface import IATTopic

from zope import schema
from zope.formlib import form
from zope.component import getMultiAdapter

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.portlets.cache import render_cachekey
from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize

from Acquisition import aq_inner

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.relateditems import RelatedItemsMessageFactory as _

try:
    from collective.contentleadimage.config import IMAGE_FIELD_NAME
    from collective.contentleadimage.leadimageprefs import ILeadImagePrefsForm
    from zope.component import getUtility
    from Products.CMFPlone.interfaces import IPloneSiteRoot
    LEADIMAGE_EXISTS = True
except ImportError:
    LEADIMAGE_EXISTS = False


_N_CHAR = 100

DEFAULT_ALLOWED_TYPES = (
    'News Item',
    'Document',
    'Event',
    'File',
    'Image',
)


# used to sanitize search
def quotestring(s):
    return '"%s"' % s


def quote_bad_chars(s):
    bad_chars = ["(", ")"]
    for char in bad_chars:
        s = s.replace(char, quotestring(char))
    return s


class IRelatedItems(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    portlet_title = schema.TextLine(
        title=_(u'Portlet title'),
        description=_(u'Title in portlet.'),
        required=True,
        default=_(u'Related Items')
    )

    count = schema.Int(
        title=_(u'Number of related items to display'),
        description=_(u'How many related items to list.'),
        required=True,
        default=10
    )

    states = schema.Tuple(
        title=_(u"Workflow state"),
        description=_(u"Items in which workflow state to show."),
        default=('published', ),
        required=True,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.WorkflowStates"
        )
    )

    allowed_types = schema.Tuple(
        title=_(u"Allowed Types"),
        description=_(u"Select the content types that should be shown."),
        default=DEFAULT_ALLOWED_TYPES,
        required=True,
        value_type=schema.Choice(
            vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"
        )
    )

    show_all_types = schema.Bool(
        title=_(u"Show all types in 'more' link"),
        description=_(u"If selected, the 'more' link will display "
                       "results from all content types instead of "
                       "restricting to the 'Allowed Types'."),
        default=False,
    )

    only_subject = schema.Bool(
        title=_(u"Search only on subject"),
        description=_(u"If selected, we will search only on content subject."),
        default=False,
    )

    display_all_fallback = schema.Bool(
        title=_(u"Display recent items on no results fallback"),
        description=_(u"If selected, we will display all "
                      "allowed items where there are no results for "
                      "our current related items query"),
        default=True,
    )

    display_description = schema.Bool(
        title=_(u"Display description"),
        description=_(
            u"If selected, we will show the content short description"),
        default=True,
    )
    """"
    show_recent_items = schema.Bool(
        title=_(u"Show recent items"),
        description=_(u"If selected, recent items are shown "
                       #"results from all content types instead of "
                       "when related items are not found'."),
        default=False,
    )
    """


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IRelatedItems)

    def __init__(self,
                 portlet_title=u'Related Items',
                 count=5,
                 states=('published',),
                 allowed_types=DEFAULT_ALLOWED_TYPES,
                 #show_recent_items=False,
                 only_subject=False,
                 show_all_types=False,
                 display_description=True,
                 display_all_fallback=True,
                ):
        self.portlet_title = portlet_title
        self.count = count
        self.states = states
        self.allowed_types = allowed_types
        self.only_subject = only_subject
        #self.show_recent_items = show_recent_items
        self.show_all_types = show_all_types
        self.display_description = display_description
        self.display_all_fallback = display_all_fallback

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return self.portlet_title or _(u"Related Items")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """
    _template = ViewPageTemplateFile('relateditems.pt')

    @ram.cache(render_cachekey)
    def render(self):
        return xhtml_compress(self._template())

    @property
    def available(self):
        return len(self._data())

    def getRelatedItems(self):
        return self._data()

    @property
    def showRelatedItemsLink(self):
        """Determine if the 'more...' link needs to be displayed
        """
        # if the more link is for all types then always show it
        if self.data.show_all_types:
            return True
        # if we have more results than are shown, show the more link
        elif len(self.all_results) > self.data.count:
            return True
        return False

    def hasLeadImage(self):
        return LEADIMAGE_EXISTS

    def itemHasLeadImage(self, item):
        if self.hasLeadImage():
            return item.hasContentLeadImage

    def currenttime(self):
        return time.time()

    @property
    def prefs(self):
        res = ''
        if LEADIMAGE_EXISTS:
            portal = getUtility(IPloneSiteRoot)
            res = ILeadImagePrefsForm(portal)
        return res

    #used for the view (relateditems.pt)
    def tag(self, obj, css_class='tileImage'):
        if LEADIMAGE_EXISTS:
            context = aq_inner(obj)
            field = context.getField(IMAGE_FIELD_NAME)
            if field is not None:
                if field.get_size(context) != 0:
                    scale = 'thumb'  # self.prefs.desc_scale_name
                    return field.tag(context, scale=scale, css_class=css_class)
        return ''

    def getAllRelatedItemsLink(self):
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        portal_url = portal_state.portal_url()
        context = aq_inner(self.context)
        req_items = {}
        # make_query renders tuples literally, so let's make it a list
        req_items['Subject'] = list(context.Subject())
        if not self.data.show_all_types:
            req_items['portal_type'] = list(self.data.allowed_types)
        return '%s/search?%s' % (portal_url, make_query(req_items))

    def trimDescription(self, desc):
        if len(desc) > _N_CHAR:
                res = desc[0:_N_CHAR]
                lastspace = res.rfind(" ")
                res = res[0:lastspace] + " ..."
                return res
        else:
                return desc

    def _contents(self):
        contents = []
        # Collection
        if IATTopic.providedBy(self.context):
            try:
                contents = self.context.queryCatalog(
                contentFilter={'sort_limit': 6})
            except:
                pass
        # probably a folder
        else:
            contents = self.context.getFolderContents()

        # Make sure the content is not too big
        contents = contents[:6]

        return contents

    def _itemQuery(self, value):
        search_query = []

        # Include categories in the search query
        #keywords = map(lambda x: x.lower(), value.Subject())
        keywords = list(value.Subject())

        # Include words from title in the search query
        title = value.Title().split()

        search_query = title + keywords

        # Filter out boolean searches and keywords with only one letter
        search_query = [res
                        for res in search_query
            if not res.lower() in ['not', 'and', 'or'] and len(res) != 1]

        return search_query

    def _itemsQuery(self, values):
        query = ''
        items = []
        for item in values:
            items += self._itemQuery(item)

        # remove duplicated search keywords
        items = self.uniq(items)

        #if len(items):
        #    query = items.pop(0)

        query = " OR ".join(items)

        return query

    def uniq(self, alist):    # Fastest order preserving
        set = {}
        return [set.setdefault(e, e) for e in alist if e not in set]

    def _query(self):
        context = aq_inner(self.context)

        contents = [self.context]
        # TODO: test if a collection limited to 3 items show anything...
        # get items in folder or collection
        folder_contents = []
        if self.context.isPrincipiaFolderish:
            folder_contents = self._contents()
            folder_contents = map(lambda x: x.getObject(), folder_contents)
        else:
            # Add references and back-references (related items)
            try:
                contents += context.getReferences()
            except Exception:
                pass
            try:
                contents += context.getBackReferences()
            except Exception:
                pass

        contents += folder_contents

        search_query = self._itemsQuery(contents)
        return search_query

    def getPortletTitle(self):
        return self.data.portlet_title

    def displayDescription(self):
        return self.data.display_description

    @memoize
    def _data(self):
        plone_tools = getMultiAdapter((self.context, self.request),
                                      name=u'plone_tools')
        context = aq_inner(self.context)
        here_path = ('/').join(context.getPhysicalPath())

        # Exclude items from related if contained in folderish
        content = []
        if self.context.isPrincipiaFolderish:
            content = self._contents()

        exclude_items = map(lambda x: x.getPath(), content)
        exclude_items += [here_path]

        search_query = self._query()
        search_query = quote_bad_chars(search_query)
        #print 'search_query = '+search_query

        catalog = plone_tools.catalog()
        limit = self.data.count
        # increase by one since we'll get the current item
        extra_limit = limit + len(exclude_items)

        query = dict(portal_type=self.data.allowed_types,
                     SearchableText=search_query,
                     sort_limit=extra_limit)
        if self.data.only_subject:
            query['Subject'] = self.context.Subject()
            if 'SearchableText' in query:
                del query['SearchableText']
        results = catalog(**query)

        # filter out the current item
        self.all_results = [res
                            for res in results
                            if not res.getPath() in exclude_items]

        # No related items were found
        # Get the latest modified articles

        #if self.data.show_recent_items and self.all_results == []:
        if self.data.display_all_fallback and (self.all_results == []):
            results = catalog(portal_type=self.data.allowed_types,
                              sort_on='modified',
                              sort_order='reverse',
                              sort_limit=extra_limit)
            self.all_results = [res
                                for res in results
                                if not res.getPath() in exclude_items]

        return self.all_results[:limit]


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IRelatedItems)
    label = _(u"Add Related Items Portlet")
    description = _(u"This portlet displays recent Related Items.")

    def create(self, data):
        return Assignment(
            portlet_title=data.get('portlet_title', u'Related Items'),
            count=data.get('count', 5),
            states=data.get('states', ('published',)),
            allowed_types=data.get('allowed_types',
                                   DEFAULT_ALLOWED_TYPES),
            #show_recent_items=data.get('show_recent_items', False),
            only_subject=data.get('only_subject', False),
            show_all_types=data.get('show_all_types', False),
            display_all_fallback=data.get('display_all_fallback', True),
            display_description=data.get('display_description', True),
        )


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IRelatedItems)
    label = _(u"Edit Related Items Portlet")
    description = _(u"This portlet displays related items based on "
                     "keywords matches, title and related items.")
