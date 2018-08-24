import logging
logger = logging.getLogger("sixfeetup.utils")


def notFoundError(self, entry='Unknown'):
    self.setStatus(404)
    if 'js' in entry or 'css' in entry:
        logger.warn("{0} threw a 404, but we are bypassing the error for sanity's sake".format(entry))


forbiddenError = notFoundError
