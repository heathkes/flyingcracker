import fc3

VERSION = (0, 2, None)

def get_version():
    "Returns the version as a human-format string."
    v = '.'.join([str(i) for i in VERSION[:-1]])
    
    from django.utils.version import get_svn_revision
    path = fc3.__path__[0]
    svn = get_svn_revision(path)
    
    if VERSION[-1]:
        v = '%s-%s-%s' % (v, VERSION[-1], svn)
    else:
        v = '%s-%s' % (v, svn)
    return v
