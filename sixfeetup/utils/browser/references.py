from zope.interface import implementer, Interface
from ZTUtils import LazyFilter
from Products.Five import BrowserView


class IReferenceUtils(Interface):
    """Some utilities to get properly filtered refs
    """

    def getFilteredRefs(obj, relationship, sort_on, reverse):
        """Get the references for an object and pass them through
        """

    def getFilteredBRefs(obj, relationship, sort_on, reverse):
        """Get the back references for an object and pass them through
        """

    def getFilteredOrderedRefs(obj, relationship, reverse):
        """Get ordered refs back from an OrderableRefField
        """

    def getFilteredOrderedBRefs(obj, relationship, reverse):
        """Get ordered BRefs back from an OrderableRefField
        """


class ReferenceUtils(BrowserView):
    """see IReferenceUtils for documentation
    """
    implementer(IReferenceUtils)

    def _processRefs(self, refs, sort_on, reverse):
        """util method to run the refs through LazyFilter
        """
        filtered_refs = []
        if refs and refs is not None:
            if not isinstance(refs, list):
                refs = [refs]
            filtered_refs = list(LazyFilter(refs, skip='View'))
        if sort_on is not None:
            filtered_refs.sort(lambda x, y: cmp(x.getField(sort_on).get(x),
                                                y.getField(sort_on).get(y)))
            if reverse:
                filtered_refs.reverse()
        return filtered_refs

    def getFilteredRefs(self, obj, relationship, sort_on=None, reverse=False):
        """see IReferenceUtils for documentation
        """
        refs = obj.getRefs(relationship)
        return self._processRefs(refs, sort_on, reverse)

    def getFilteredBRefs(self, obj, relationship, sort_on=None, reverse=False):
        """see IReferenceUtils for documentation
        """
        refs = obj.getBRefs(relationship)
        return self._processRefs(refs, sort_on, reverse)

    def getFilteredOrderedRefs(self, obj, relationship, reverse=False):
        refs = obj.getReferenceImpl(relationship)
        refs.sort(
            lambda a, b: cmp(getattr(a, 'order', None), getattr(b, 'order', None)))
        ref_objs = [ref.getTargetObject() for ref in refs]
        return self._processRefs(ref_objs, None, reverse)

    def getFilteredOrderedBRefs(self, obj, relationship, reverse=False):
        refs = obj.getBackReferenceImpl(relationship)
        refs.sort(
            lambda a, b: cmp(getattr(a, 'order', None), getattr(b, 'order', None)))
        ref_objs = [ref.getTargetObject() for ref in refs]
        return self._processRefs(ref_objs, None, reverse)
