"""Setup handlers for setting PropertyManager properties on arbitrary
objects."""

from zope.interface import Interface
from zope.interface import directlyProvides

from Products.GenericSetup.utils import importObjects
from Products.GenericSetup.utils import exportObjects

from Products.CMFCore.interfaces import ISiteRoot

from Products.CMFPlone.exportimport.propertiestool import (
    SimpleItemWithPropertiesXMLAdapter, )

class IObjectPropertiesSetupEnviron(Interface):
    pass

class ObjectPropertiesXMLAdapter(SimpleItemWithPropertiesXMLAdapter):
    """Just a starting point for ISite."""
    
    __used_for__ = ISiteRoot

    name = 'objectproperties'

def importObjectProperties(context):
    """Import arbitrary object properties from XML files."""
    directlyProvides(context, IObjectPropertiesSetupEnviron)
    site = context.getSite()
    importObjects(site, '', context)

def exportObjectProperties(context):
    """Export arbitrary object properties as a set of XML files."""
    directlyProvides(context, IObjectPropertiesSetupEnviron)
    site = context.getSite()
    exportObjects(site, '', context)
