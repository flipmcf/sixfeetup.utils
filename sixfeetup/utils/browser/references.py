from zope.interface import implements, Interface
from ZTUtils import LazyFilter
from Products.Five import BrowserView


class IReferenceUtils(Interface):
    """Some utilities to get properly filtered refs
    """

    def getFilteredRefs(obj, relationship, sort_on):
        """Get the references for an object and pass them through
        """
    
    def getFilteredBRefs(obj, relationship, sort_on):
        """Get the back references for an object and pass them through
        """


class ReferenceUtils(BrowserView):
    """see IReferenceUtils for documentation
    """
    implements(IReferenceUtils)
    
    def _processRefs(refs, sort_on):
        """util method to run the refs through LazyFilter
        """
        filtered_refs = []
        if refs and refs is not None:
            if not isinstance(list, refs):
                refs = [refs]
            filtered_refs = list(LazyFilter(refs, skip='View'))
        if sort_on is not None:
            filtered_refs.sort(lambda x, y: cmp(x.getField(sort_on).get(x),
                                                y.getField(sort_on).get(y)))
        return filtered_refs
    
    def getFilteredRefs(self, obj, relationship, sort_on=None):
        """see IReferenceUtils for documentation
        """
        filtered_refs = []
        refs = obj.getRefs(relationship)
        return self._processRefs(refs, sort_on)
    
    def getFilteredBRefs(self, obj, relationship, sort_on=None):
        """see IReferenceUtils for documentation
        """
        filtered_refs = []
        refs = obj.getBRefs(relationship)
        return self._processRefs(refs, sort_on)
