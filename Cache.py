"""
TODO:
- Reimplement NODIR
- Option to merge path elements into one directory while file count
  is below treshold.
"""
import time, os, sys
import re

import Params
import Runtime
import Rules
from util import *


def load_backend_type(tp):
    assert '.' in tp, "Specify backend as <module>.<backend-type>"
    p = tp.split( '.' )
    path, name = '.'.join( p[:-1] ), p[-1]
    mod = __import__( path, locals(), globals(), [] )
    return getattr( mod, name )


def suffix_ext(path, suffix):
    x = re.match('.*\.([a-zA-Z0-9]+)$', path)
    if x:
        p = x.start(1)
        path = path[:p-1] + suffix + path[p-1:]
    else:
        path += suffix
    return path      


class File(object):

    """
    Simple cache that stores at path/filename taken from URL.
    The PARTIAL suffix (see Params) is used for partial downloads.

    Parameters ARCHIVE and ENCODE_PATHSEP also affect the storage location.
    ARCHIVE is applied after ENCODE_PATHSEP.
    """

    def __init__(self, path=None):
        """
        The path is an `wget -r` path. Meaning it has the parts:
        host/path?query. The cache implementation will determine the final
        local path name. 
        """
        super( File, self ).__init__()
        self.partial = None
        self.full = None
        self.file = None
        if path:
            self.init(path)

    def init(self, path):
        assert Params.PARTIAL not in path

        assert not path.startswith(os.sep), \
                "File.init: saving in other roots not supported,"\
                " only paths relative to Runtime.ROOT allowed."

        # encode query and/or fragment parts
        sep = min_pos(path.find('#'), path.find( '?' ))
        # optional removal of directories in entire path
        psep = Runtime.ENCODE_PATHSEP
        if psep:
            path = path.replace( '/', psep)
        else:
            # partial pathsep encode
            if sep != -1:
                path = path[ :sep ] + path[ sep: ].replace( '/', psep)
        # make archive path
        if Runtime.ARCHIVE:
            path = time.strftime( Runtime.ARCHIVE, time.gmtime() ) + path
       
        assert Runtime.PARTIAL not in path

        # add default part
        if path[-1] == os.sep:
            path += Params.DEFAULT

        self.path = path

        get_log(Params.LOG_DEBUG)('%s: init %s', self, path)
        self.file = None

        assert len(self.abspath()) < 255, \
                "LBYL, cache location path to long for Cache.File! "

        self.stat()

    def full_path(self):
        assert Runtime.ROOT
        return os.path.join( Runtime.ROOT, self.path )

    def partial_path(self):
        assert Runtime.PARTIAL
        return suffix_ext( self.full_path(), Runtime.PARTIAL )

    def stat( self ):
        assert Runtime.PARTIAL not in self.path
        abspath = self.full_path()
        partial = self.partial_path()
        if os.path.isfile( partial ):
            self.full = False
            self.partial = os.stat( partial )
        elif os.path.isfile( abspath ):
            self.full = os.stat( abspath )
            self.partial = False
        return self.partial or self.full

    def abspath( self ):
        assert Runtime.PARTIAL not in self.path, self.path
        if not (self.partial or self.full):
            self.stat()
        if self.full:
            return self.full_path()
        else:
            return self.partial_path()

    @property
    def size( self ):
        stat = ( self.partial or self.full )
        if stat:
            return stat.st_size

    @property
    def mtime(self):
        stat = ( self.partial or self.full )
        if stat:
            return stat.st_mtime

    def utime(self, mtime):
        os.utime( self.abspath(), ( mtime, mtime ) )
        self.stat()

    def open_new( self ):
        assert not self.file

        get_log(Params.LOG_NOTE, 'cache')\
                ('%s: Preparing new file in cache', self)
    
        new_file = self.abspath()
        
        tdir = os.path.dirname( new_file )
        if not os.path.exists( tdir ):
            os.makedirs( tdir )

        try:
            self.file = open( new_file, 'w+' )
        except Exception, e:
            get_log(Params.LOG_NOTE, 'cache')\
                    ('%s: Failed to open file: %s', self, e)
            self.file = os.tmpfile()

    def open_partial( self, offset=-1 ):
        assert not self.file
        self.file = open( self.abspath(), 'a+' )
        if offset >= 0:
            assert offset <= self.tell(), 'range does not match file in cache'
            self.file.seek( offset )
            self.file.truncate()
        get_log(Params.LOG_INFO, 'cache')\
                ('%s: Resuming partial file in cache at byte %s', self, self.tell())

    def open_full( self ):
        assert not self.file
        self.file = open( self.abspath(), 'r' )
#        self.size = self.tell()

    def open( self ):
        if self.full:
            self.open_full()
        elif self.partial:
            self.open_partial()
        else:
            self.open_new()

    def remove_full( self ):
        os.remove( self.abspath() )
        get_log(Params.LOG_NOTE, 'cache')\
                ('%s: Removed complete file from cache', self)

    def remove_partial( self ):
        get_log(Params.LOG_NOTE, 'cache')\
                ('%s: Removed partial file from cache', self)
        os.remove( self.abspath() + Runtime.PARTIAL )

    def read( self, pos, size ):
        self.file.seek( pos )
        return self.file.read( size )

    def write( self, chunk ):
        self.file.seek( 0, 2 )
        return self.file.write( chunk )

    def tell( self ):
        self.file.seek( 0, 2 )
        return self.file.tell()

    def close( self ):
        assert self.file
        self.file.close()
        self.file = None
        self.partial, self.full = None, None

#    def __nonzero__(self):
#      return ( self.complete() or self.partial ) != None

    def __del__( self ):
      if self.file:
          try:
              self.close()
          except Exception, e:
              get_log(Params.LOG_WARN)\
                      ("%s: Error on closing cache file: %s", self, e)

