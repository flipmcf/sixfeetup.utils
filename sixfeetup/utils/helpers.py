import logging
from DateTime import DateTime
from Testing.makerequest import makerequest
from Products.CMFCore.utils import getToolByName
from Products.GenericSetup.upgrade import _upgrade_registry
from Products.GenericSetup.registry import _profile_registry
from Products.CMFPlone.utils import base_hasattr
from Products.GenericSetup.context import DirectoryImportContext


logger = logging.getLogger(__name__)

#####################################################
# Random bits and pieces of code that could be useful

def getSiteObj(site):
    """Return a site object depending on whether it is a 
    import context or a upgrade step context
    """
    if isinstance(site, DirectoryImportContext):
        return site.getSite()
    return getToolByName(site, 'portal_url').getPortalObject()
    
def getPortalObj(context):
    """Is this really necessary?  Use @@plone_<helpers>?
    """
    return getToolByName(context, 'portal_url').getPortalObject()

def dateForProcessForm(field, field_date, form_dict=None):
    """Take a DateTime object or string and convert it into the keys that
    processForm expects
    
    If form_dict is not passed in a dictionary will be passed back. Otherwise
    the form dictionary will be updated.
    """
    if not isinstance(field_date, DateTime):
        field_date = DateTime(field_date)
    will_return = False
    if form_dict is None:
        will_return = True
        form_dict = {}
    form_dict[field] = field_date.ISO()
    form_dict['%s_year' % field] = field_date.year()
    form_dict['%s_month' % field] = field_date.month()
    form_dict['%s_day' % field] = field_date.day()
    form_dict['%s_hour' % field] = field_date.hour()
    form_dict['%s_minute' % field] = field_date.minute()
    if not will_return:
        return
    return form_dict

######################################################
# Helpers for GenericSetup upgrades and setup handlers

def updateCatalog(portal):
    """Update the catalog
    """
    logger.info('****** updateCatalog BEGIN ******')
    pc = getToolByName(portal, 'portal_catalog')
    pc.refreshCatalog()
    logger.info('****** updateCatalog END ******')
    
def clearAndRebuildCatalog(portal):
    """Clear and rebuild the catalog
    """
    logger.info('****** clearAndRebuildCatalog BEGIN ******')
    pc = getToolByName(portal, 'portal_catalog')
    pc.clearFindAndRebuild()
    logger.info('****** clearAndRebuildCatalog END ******')

def updateSecurity(portal):
    """Run the update security on the workflow tool"""
    logger.info('****** updateSecurity BEGIN ******')
    wtool = getToolByName(portal, 'portal_workflow')
    wtool.updateRoleMappings()
    logger.info('****** updateSecurity END ******')

# GenericSetup forces a redirect on some of these methods, we are
# basically rewriting them here without that.
def deleteImportSteps(portal, ids):
    """Remove a list of import step IDs
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    for step_id in ids:
        try:
            setup_tool._import_registry.unregisterStep(step_id)
        except KeyError:
            logger.info('Could not remove import step: %s' % step_id)
    setup_tool._p_changed = True

def deleteExportSteps(portal, ids):
    """Remove a list of export step IDs
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    for step_id in ids:
        try:
            setup_tool._export_registry.unregisterStep(step_id)
        except KeyError:
            logger.info('Could not remove import step: %s' % step_id)
    setup_tool._p_changed = True

def runUpgradeSteps(site, profile_id):
    """run the upgrade steps for the given profile_id in the form of:
    
    profile-<package_name>:<profile_name>
    
    example:
    
    profile-my.package:default
    
    Basically this is the code from GS.tool.manage_doUpgrades() in step
    form.  Had to extract the code because it was doing a redirect back to the
    upgrades form in the GS tool.
    """
    setup_tool = getToolByName(site, 'portal_setup')
    logger.info('****** runUpgradeSteps BEGIN ******')
    upgrade_steps = setup_tool.listUpgrades(profile_id)
    steps_to_run = []
    for step in upgrade_steps:
        if isinstance(step, list):
            # this is a group of steps
            for new_step in step:
                steps_to_run.append(new_step['step'].id)
        else:
            steps_to_run.append(step['step'].id)
    
    #################
    # from GS tool...
    ##################
    for step_id in steps_to_run:
        step = _upgrade_registry.getUpgradeStep(profile_id, step_id)
        if step is not None:
            step.doStep(setup_tool)
            msg = "Ran upgrade step %s for profile %s" % (step.title,
                                                          profile_id)
            logger.info(msg)

    # XXX should be a bit smarter about deciding when to up the
    #     profile version
    profile_info = _profile_registry.getProfileInfo(profile_id)
    version = profile_info.get('version', None)
    if version is not None:
        setup_tool.setLastVersionForProfile(profile_id, version)

    logger.info('****** runUpgradeSteps END ******')

def publishEverything(site, path=None, transition='publish', recursive=True):
    """Publishes all content that has the given transition
    
    Pass in a PhysicalPath to publish a specific section
    """
    portal = getSiteObj(site)
    pc = getToolByName(portal, 'portal_catalog')
    query = {}
    if path is None:
        query['path'] = "/%s" % portal.id
    else:
        query['path'] = path
    if not recursive:
        query['path'] = {'query': query['path'], 'depth': 0}
    res = pc(query)
    for result in res:
        obj = result.getObject()
        try:
            obj.portal_workflow.doActionFor(
                obj,
                transition,
                comment='Content published automatically'
            )
        except:
            logger.debug("\ncouldn't publish %s\n**********\n" % obj.Title())

def runMigrationProfile(portal, profile_id):
    """Run a migration profile as an upgrade step
    
    profile_id in the form::
    
      profile-<package_name>:<profile_name>
    
    example::
    
      profile-my.package:migration-2008-09-23
    """
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile(profile_id)

def clearLocks(portal, path=None, recursive=True):
    """Little util method to clear locks on a given path
    
    Pass in a PhysicalPath to restrict to a specific section
    """
    pc = getToolByName(portal, 'portal_catalog')
    query = {}
    if path is None:
        query['path'] = "/%s" % portal.id
    else:
        query['path'] = path
    if not recursive:
        query['path'] = {'query': query['path'], 'depth': 0}
    res = pc(query)
    for item in res:
        obj_path = '/'.join(item.getObject().getPhysicalPath())
        lock_info = '%s/@@plone_lock_info' % obj_path
        locked = portal.restrictedTraverse(lock_info).is_locked()
        if locked:
            lock_ops = '%s/@@plone_lock_operations' % obj_path
            portal.restrictedTraverse(lock_ops).force_unlock(redirect=False)

def addUserAccounts(portal, member_dicts=[]):
    """Add user accounts into the system
    
    Member dictionaries are in the following format::
    
      {
        'id': 'joeblow',
        'password': '12345',
        'roles': ['Manager', 'Member'],
        'properties': {
          'email': 'joe@example.com',
          'fullname': 'Joe Blow',
          'username': 'joeblow',
         }
      }
    
    Additional properties can be added in the properties item and will
    be passed along to the registration tool.
    """
    rtool = getToolByName(portal, 'portal_registration')
    rta = rtool.addMember
    for mem in member_dicts:
        try:
            rta(
                id=mem['id'],
                password=mem['password'],
                roles=mem['roles'],
                properties=mem['properties'],
            )
        except ValueError:
            msg = '\nlogin id %s is already taken...\n*********\n' % mem['id']
            logger.debug(msg)

def addRememberUserAccounts(portal,
                            member_dicts=[],
                            initial_transition="register_private",
                            send_emails=False):
    """Add remember user accounts into the system
    
    Member dictionaries are in the following format::
    
      {
        'id': 'joeblow',
        'fullname': 'Joe Blow',
        'email': 'joe@example.com',
        'password': '12345',
        'confirm_password': '12345',
        'roles': ['Manager'],
      }
    
    You can pass in more 'fieldName': 'values' in the dictionary, they will be
    passed on to processForm.
    
    initial_transition is the member workflow transition you want to run on 
    the members
    
    If send_emails is True then registration emails will be sent out to the users
    """
    # store the current prop
    current_setting = portal.validate_email
    if not send_emails:
        # Turn off email validation
        portal.validate_email = 0
    mdata = getToolByName(portal, 'portal_memberdata')
    wftool = getToolByName(portal, 'portal_workflow')
    existing_members = mdata.contentIds()
    for mem in member_dicts:
        if mem['id'] not in existing_members:
            mdata.invokeFactory('Member', id=mem['id'])
            new_member = getattr(mdata, mem['id'])
            # remove id as it's already set
            del mem['id']
            # finalize creation of the member
            new_member.processForm(values=mem)
            # now we can register the member since it is 'valid'
            # XXX this may be specific to the approval workflow...
            wftool.doActionFor(new_member, initial_transition)
            # reindex again to update the state info in the catalog
            new_member.reindexObject()
        else:
            msg = '\nlogin id %s is already taken...\n*********\n' % mem['id']
            logger.debug(msg)
    # but the property back
    portal.validate_email = current_setting

def updateSchema(portal,
                 update_types=[],
                 update_all=False,
                 remove_inst_schemas=True):
    """Update archetype schemas for specific types
    
    The update types is a list of strings like the following::
    
      <product_or_package>.<meta_type>
    
    Examples::
    
      ATContentTypes.ATDocument
      my.package.SomeType
    """
    portal = makerequest(portal)
    req = portal.REQUEST
    req.form['update_all'] = update_all
    req.form['remove_instance_schemas'] = remove_inst_schemas
    for obj_type in update_types:
        req.form[obj_type] = True
    portal.archetype_tool.manage_updateSchema(req)

def setPolicyOnObject(obj, policy_in=None, policy_below=None):
    """Set the placeful workflow policy on an object
    
    obj is the object we want to set the policy on
    
    policy_in is the policy set only on the obj
    
    policy_below is the policy set on all the items below obj
    """
    placeful_workflow = getToolByName(obj, 'portal_placeful_workflow')
    if not base_hasattr(obj, '.wf_policy_config'):
        obj.manage_addProduct['CMFPlacefulWorkflow'].manage_addWorkflowPolicyConfig()
        config = placeful_workflow.getWorkflowPolicyConfig(obj)
        if policy_in is not None:
            config.setPolicyIn(policy=policy_in)
        if policy_below is not None:
            config.setPolicyBelow(policy=policy_below)

def runPortalMigration(site):
    """Run any migrations that are pending
    """
    portal = getSiteObj(site)
    pm = getToolByName(site, 'portal_migration')
    if pm.needUpgrading():
        pm.upgrade()

def removeCustomFolderContent(site):
    """Remove everything in portal_skins/custom
    """
    skins_tool = getToolByName(site, 'portal_skins')
    cf = skins_tool.custom
    cf_ids = cf.objectIds()
    # goodbye EVIL!!!
    cf.manage_delObjects(cf_ids)
