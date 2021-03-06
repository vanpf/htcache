:parent project: http://freshmeat.net/projects/http-replicator
:homepage: http://github.com/dotmpe/htcache

**htcache** aims to be a versatile caching and rewriting HTTP and FTP proxy
in Python. It is a fork of http-replicator 4.0 alpha 2. See CHANGELOG.

This serves as a technical (design) documentation.
Various road signs are given up until section _`Design`, 
there starts the real specifications.

Versions
--------
Branches
    master
        - Trying to keep it steady.
        - Does currently not run stable continuously.
        - Intend to get sqlstore back into master once that matures, then see
          about other branches.  

    test
        - Must make this unstable branch.

    dev*
        - Main dev is integration of other development.

        dev_cachemaint (current)
            Cache maintenance routines.

            - ``--check-cache --prune`` remove invalid descriptors.
            - ``--check-tree --prune`` remove files without descriptor.

            - TODO: ``--keep-cache`` mark location revisioning
            - TODO: ``--validate-tree`` resource cache should match size, checksum
            - TODO: ``--validate-joinlist`` resource should have been rewritten
            - TODO: ``--validate-joinlist --auto`` rename if possible
            - TODO: ``--validate-lists`` 
            - TODO: ``--check-joinlist`` run testlines from JOIN,  
            - TODO: ``--check-lists``
            - TODO: abstract, refactor query/maintenance mode handling. Allow
              proxy request.
            - TODO: ``--print-allrecords`` simply dump?
            - TODO: ``--print-record`` query
            - TODO: ``--print-records`` query
            - TODO: ``--print-media`` query
        dev_proxyreq
            :test-protocol:
              - (dandy) 5 passed checks, 16 errors  
            :unit-tests:
              - (dandy) 35 passed checks, 8 errors
            - Maybe write a lower level protocol to interrogate the proxy about
              its downloads. See ProxyProtocol class.
            - in sync with master, dev_proxyreq, dev_domaindb
        dev_cacherev
            - Revision certain resources, always keeping a once retrieved and
              served version.
        dev_relstore
            - (dandy) 35 passed checks, 8 errors
            :unit-test:  
                - (dandy) 36 passed checks, 7 errors  

            Need to get simple relational storage.  This is suspended in favor
            of dev_sqlstore
        dev_dhtmlui
            - this injects JS, carefil to merge while Params is not externalized/contained.
            - in sync with master, dev_proxyreq, dev_domaindb
        dev_domaindb
            :system-test:
                - (dandy) 4 passed checks, 23 errors
            - add card index for URL's something like a step-up to a bookmark manager
            - in sync with master, dev_proxyreq
        dev_sqlstore
            - Working on SA backend.
            - Need to get chunked transport working again and test from there.  

    dev
        - New reintegration of previous branches
        - Now also running on iris (old debian) but with more errors.  
    dev_cachemaint
        - Work on command line cache maintenance.


.. contents::

History
-------
v0.3
    42 tests, 1 failure.

See changelog for details.

Status
------
Todo
 - (auto) remove descriptors after manual path delete.
 - use strict and other modes, adhere to RFC 2616:

   - calculate Age field [14.6]
   - don't cache Authorization response [14.8]
   - Cacheability: expiration [13.2]  
   - Cache-Control [14.9]

 - rules.join rewrites paths (to simplify, remove session id and other query meta vars)
 - rules.proc defers to external script.. or fifo? How to pass message: parsing should be easy enough to write ie. bash script.
 - javascript bookmarklet alike link for (x)HTML: enable in browser functions.

   - work on current or pointer selected resource

     - add new drop/nocache/capture/join rule
     - view version history
     - view navigation history
     - set favicon  
     - tag/annotation possible; see proc rules
     - set title based on pattern, format?

   - display hidden features in select mode  
   - browse static page
   - proxy config?
   - reload proxy

 - rules.sort prefixes paths
 - would be nice to let addon's provide new rules.
   Ex: user- or community provided favicons.

Issues
 1. Dropped connections/failure to write to client happens, but does not appear
    to be malignant. See Known errors 1.
 2. Some date headers in the wild still fail to parse.
 3. HTML placeholder served for all connections (e.g. also for flash, images)
 4. There is a version with other cl-options, it uses stdlib asyncore
    check:

    * http://web.archive.org/web/20070816213819/gertjan.freezope.org/replicator/http-replicator
    * http://web.archive.org/web/20071214200800/gertjan.freezope.org/replicator

 5. Embedded youtube does not work, but the site runs fine.

Known errors
 1. Writing to client may fail sometimes because of a dropped connection. Ie.
    Google Chrome establishes a pool of connections upon each request to speed
    up browsing, which will time out and close if not used.

Unittests
 No known failures.

Installation
------------
Start as any Python script, or:

- cp/link htcache into ``/usr/bin``
- cp/link ``init.sh`` into ``/dev/init.d/``, modify htcache flags as needed.
  Make sure paths in init.sh and Params.py are accessible.
- add line ``/etc/init.d/htcache start`` to ``/etc/local`` for
  on-startup initialization.

See http://www.debian-administration.org/articles/28 for Debian specifics.

Also create files in /etc/htcache:

* rules.drop
* rules.nocache
* rules.sort

Configuration
~~~~~~~~~~~~~
There is no separate configuration file, see Params.py and init.sh for
option arguments to the program, and for their default settings. Other settings
are given in the rewrite and rules files described before.

The programs options are divided in three parts, the first group affects
the proxy server, which is the default action.

User/system settings are provided using GNU/POSIX Command Line options.
These are roughly divided in three parts; the first group affects
the proxy server, which is the default action. The other two query or process
cached data, and are usefull for maintenance. Note that maintenance may need
exclusive write access to the cache and descriptor backends, meaning don't run
with active proxy.

See ``htcache [-h|--help]``.

Backends
_____________
htcache uses a file-based Cache which may produce a file-tree similar to
that of ``wget -r``.
This can create problems with long filenames and the characters that appear
in the various URL parts. 

Additional backends can deal with this issue (``--cache TYPE``).
The default backend was Cache.File which is compatible with ``wget -r`` but
is inadequate for general use as web proxy. The new default caches.FileTreeQ
combines some aspects desirable to deal with a wider range of resources.

- XXX: caches.FileTreeQ - encodes each query argument into a separate directory,
  the first argument being prefixed with '?'. 

- caches.FileTreeQH - Converts query into a hashsum. This one makes a bit more
  sense because queries are not hierarchical. The hashsum is encoded to a
  directory, the name prefixed with '#'.

- caches.PartialMD5 - only encodes the excess part of the filename, the limit
  being hardcoded to 256 characters.

- caches.FileTree - combines above three methods.

- caches.RefHash - simply encodes full URI into MD5 hex-digest and use as
  filename. Simple but effective.

Cache options
________________
The storage location is futher affected by ``--archive`` and ``--nodir``.

Regular archival of a resources is possible by prefixing a formatted date to
the path. Ie. '%Y/%M/%d' would store a copy and maintain updates of a
resource for every day. Prefixing a timestamp would probably store a new copy
for each request.

This option (``--archive FMT``) results in lots of redundant data. It also
makes static, off-line proxy operation on the resulting filesystem tree
impossible.

The nodir parameter accepts a replacement for the directory separator Nnd
stores the path in a single filename. This may affect FileTreeQ.

Logging
______________
- All std output goes through log() calls to a stream of formatted lines.
- Setting to run as daemon effectively sets the output to a std log.
- For each log() call there is a level and facility.
- The normal mode when not quiet is to emit based on error-level threshold.

- Then there is a facility filter. Needs work.
  Should 'bind facilities' on init, ie. enable them by tying them to an output.

- The facility by default is set to the origin component.
  Each component has at least one logger for itself, but can log for more
  'facilities'.

In addition to the module names, I like some more specialized facilities.
These all have their own recursive tree formatters to print specialized
information the the program structure through phases in the server handler.



These are better suited for dynamic monitoring than log events. 
Perhaps work them out as log events and use monitoring component to view them
or print tree slices when updates are sent.

request-tree::
	Request  <- Protocol     <- Response
	 \- Cache    \- Resource

client-tree::
	client  - Request  - Cache
	client  - Request +- Cache
	                  \- Protocol
	client  - Request +- Cache
	                  \- Protocol  - server
	client  - Request +- Cache
	                  \- Protocol +- server
	                              +- Resource
	                              \- Response
resource-tree::
	Cache  -  Request -  client
	Resource <-  Protocol <-+ Request  <- client
	   file <-  Cache <-/ 
		
	Resource <-+ Protocol <-+ Request  <- client
	Response <-/            |
	       file <-  Cache <-/ 



Documentation
-------------
No further manual guidance is given.

Code should document implementation, and should refer to specs given below
for specific requirements.


Design
------
XXX:
htcache client/server flow with emphasis on different types
of request and response sequences::

   .                         htcache
                             _______

                                o <-------------*get---  client
                                |
                                |---blocked(1)-------->
                                |---static(2)--------->
                                |---direct(3)--------->
   server <------------normal---|
          <------(4)rewritten---|
          <------*conditional---'

           --*normal----------> o
                                |--*nocache(8)-------->
                                ~
           ---rewritten(5)----> o
                                |---rewritten(6)------>
                                |---joined(7)--------->
                                `--*normal------------>
           ---not modified----> o 
                                |---rewritten(6)------>
                                |---joined(7)--------->
                                `--*cached------------>

           ---error-----------> o---blind(8)---------->





   * indicates wether there may be partial entity-content transfer


Normally a request creates a new cache location and descriptor, these are
the normal lines. Static responses are always served from cache, and 
conditional requests may be (these depend on HTTP cache control).

Beside these messages, also note the following special cases of request
and response messages. Not all are implemented.

== ================================================= =======================
                                                     Rules file
-- ------------------------------------------------- -----------------------
1. Dropped by proxy (blocked url)                    rules.drop
2. Static resource                                   (db & filesystem)
3. Direct URL (dynamic proxy resource)               (hardcoded)
4. Rewritten request message                         (n.i.)
5. Rewritten response message (cache rewritten)      (n.i.)
6. Rewritten response message (cache original)       rules.rewrite
7. Response joined with other resource (cache join)  rules.join
8. Blind response (uncached)                         rules.nocache
== ================================================= =======================

See the section `Rule Syntax`_ for the exact syntax.


1. Asynchronous core: Fiber
~~~~~~~~~~~~~~~~~~~~~~~~~~~
HTCache is a fork of http-replicator and the main script follows roughly the same handler
and no insignificant changes to ``fiber.py``.

It has a bit more elaborated message handling in the protocol part and renamed
some of it::

   HtRequest ----> CachingProtocol --------get--> DirectResponse (3)
                      |            `----nocache-> Blocked(Image)ContentResponse (1)
                      |            `--------ok--> DataResponse
                      |            `--------ok--> XXX:RewrittenDataResponse (6)
                      `- HttpProtocol ------ok--> (Chunked)DataResponse
                      |               `--error--> BlindResponse
                      `- FtpProtocol -----------> DataResponse
                                     `----------> NotFoundResponse

The HtRequest class reads incoming request message and determines the protocol 
for the rest of the session. Protocol will wrap the incoming data, the parsed 
request header of that data and if needed send the actual message. Upon receiving
a response it parses the message header and determines the appropiate response.

XXX: states


2. Cache backend
~~~~~~~~~~~~~~~~
There are several types from which may be instantiated. 
The type is fixed by configuration and so it may change.

The single parameter to the type is the relative path for 
which a storage is requested. 

The backend once instantiated prepares the location and then 
does a stat on any cached content present.

Its size will correspond to that of the remote resource, or
the end of the partial download.
A tag within the path indicates where the content is complete.

The content file has its mtime adjusted to the server reported Last-Modified
time. 

The file size, mtime and presence of the partial-tag is used in constructing
subsequent requests for the same resource, and should implement proper
cache validation.


3. Descriptor backend
~~~~~~~~~~~~~~~~~~~~~
Not everything about a cachable resource can be recorded on the filesystem, 
unless we use an AsIs storage and store the message entirely but obscuring its 
contents for other applications.

The storage should contain the normalized data. The exact model to be defined
along the way.

The data is created once the server reports status OK and is ready to
start transferring content.

The data supplements the file metadata primarily by the etag for cache
validation.
Perhaps the etag when better understood can be used in the Cache backend.

The data should be usable to reconstruct at least the full entity headers
without contacting the origin server. This is called static mode.

Concurrent requests for the same resource are put on hold until the 
first request commits the descriptor. Once a static initialization is possible,
subsequent requests can skip the protocol and join in on the running 
download by initializing a new response object. 

TODO: expiration


Rule Syntax
~~~~~~~~~~~
rules.drop and rules.nocache::

  # hostpath
  [^/]*expample\.net.*

Matching DROP rules deny access to the origin server, and instead serve a HTML
or image placeholder.

rules.nocache::

  # hostpath
  [^/]*gmail\.com.*

A matching NOCACHE rule bypasses the caching for a request, serving directly
from the origin server or the next proxy on the line.

Both DROP and NOCACHE rule-format will change to include matching on protocol.
Currently, both rules match on hostname and following URL parts only (hence
the [^/] pattern).

rules.{req,res,resp}.sort::

  # proto  hostpath               replacement             root
  *        (.*)                   \1
  *        [^/]*example\.net.*    canonical-example.net   mydir/

SORT rules currently prefix the cache-location with a tag, in above example the
location under ROOT for all content from `youtube.com` will be ``mydir/``. If
the ``--archive`` option is in effect it is prefixed to this tag. (Note that
``--nodir`` is applied *after prefixing*)

filter.{req,res,resp}.filter::

  # mediatype   pattern   replace
  *             (.*)      \1

This feature is under development.
Rewriting content based on above message matching is planned.

2. Internal server
~~~~~~~~~~~~~~~~~~
Beside serving in static mode (cached content directly from local storage, w/o
server header), static responses may also include content generated by the proxy
itself. In this double behaviour, it provides the following paths:

/echo
    Echo the request message.
/reload
    Reload the server, usefull while writing code.
/htcache.js
    The HTCache DHTML client may expose proxy functionality for retrieved
    content. It is included by setting Params.DHTML_CLIENT.


----

Two to three separate filesystem trees are kept beneath the cache root.

- SHA1 hashing during new resource fetch

::  

    /var/
      cache/
        sha1/
          <sha1sum>        Resource Contents
        urimd5/      
          <md5sum>/*       Timestamped symlink to contents
          <md5sum>.uriref  (optional) Normalized URI
          <md5sum>.headers (optional) As-is header storage
        archive/
          
        www/*              wget -r tree symlinking to urimd5

The first two are always applied. Storing uriref and headers could be optional.
For queries it may be nice to create indices in flat db's.
The wget tree is applied for all compatible URIs, ie. those < 256 chars.
  
XXX: could a deeper tree be created by symlinking? think so..

----

See also notes on `Cache Control <control.rst>`_

