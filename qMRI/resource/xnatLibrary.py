#!/usr/bin/python

# Created 2014-10-15, Jordi Huguet, Dept. Radiology AMC Amsterdam
# Modified 2018-03-21, Jordi Huguet, Neuroimaging ICT BBRC Barcelona

####################################
__author__      = 'Jordi Huguet'  ##
__dateCreated__ = '20141015'      ##
__version__     = '1.4'           ##
__versionDate__ = '20180321'      ##
####################################

# xnatLibrary.py
# Class with set of functionalities for interfacing/communicating with XNAT

# TO DO:
# - ...

import httplib
import urlparse
import base64
import urllib
import json
import os
import datetime
import ssl

class XNATException(Exception):
    pass

class XNAT(object):
    ''' Class with set of functionalities for interfacing/communicating with XNAT using REST API'''
    ''' To instantiate properly, provide XNAT hostname (URL) and a char string containing 'username:password' '''
    ''' A valid XNAT account is required to interface with the XNAT '''
    
    def __init__(self, hostname, usr_pwd, unverified_context=False, verbose=True):
        self.host = self.normalizeURL(hostname)
        self.b64Auth = base64.encodestring(usr_pwd).replace('\n', '')
        self.ssl_context = ssl.create_default_context()
        if unverified_context : 
            self.ssl_context = ssl._create_unverified_context()
        self.jsession = self.getJSessionID()
        self.verbose = verbose

    def __enter__(self):
        return self
    
    def __exit__(self, type, value, traceback):
        self.closeJSessionID()
    
    def normalizeURL(self, url):
        '''Check if the given URL ends or not with an slash char'''
        '''Returns a normalized URL string'''
        if url[len(url)-1] == '/' :
            url = url[:-1]
        return url
    
    def resourceExist(self,URL):
        '''HTTP query to check if a given URL already exists'''
        '''Returns an HTTP response structure'''
        
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(URL)
        
        headers = {}
        headers['Content-type'] = "application/x-www-form-urlencoded"
        headers['Accept'] = "*/*"
        headers['Cookie'] = "JSESSIONID=%s" %self.jsession
        
        if scheme == 'https' :
            connection = httplib.HTTPSConnection(netloc, timeout=10, context=self.ssl_context)
        else :
            connection = httplib.HTTPConnection(netloc, timeout=10)
            
        connection.request('HEAD', path, "", headers)
        response = connection.getresponse()
        connection.close()
        
        return response    
    
    def getXML(self, URL, options=None):
        '''Calls a XNAT REST xml resource'''
        '''Returns an XML object'''
        return self.getResource(URL, options)
        
    def getResource(self, URL, options=None):
        '''Get an XNAT resource'''
        '''Returns an object'''
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(URL)
        
        headers = {}
        headers['Content-type'] = "application/x-www-form-urlencoded"
        headers['Accept'] = "*/*"
        headers['Cookie'] = "JSESSIONID=%s" %self.jsession
        
        if scheme == 'https' :
            connection = httplib.HTTPSConnection(netloc, timeout=100, context=self.ssl_context)
        else :
            connection = httplib.HTTPConnection(netloc, timeout=100)
        
        if options != None :
            path += '?%s' % options
        connection.request('GET', path, "", headers)
            
        response = connection.getresponse()
        if response.status != 200 :
            connection.close()
            raise XNATException('HTTP response: #%s - %s' % (response.status, response.reason))
        
        responseOutput = response.read()
        connection.close()
        
        #jsonOutput = json.loads(responseOutput)
        #resultSet = jsonOutput['ResultSet']['Result']
        
        return responseOutput, response    
    
    def queryURL(self, URL, options=None):
        '''Calls a XNAT REST resource'''
        '''Returns a JSON object'''
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(URL)
        
        headers = {}
        headers['Content-type'] = "application/x-www-form-urlencoded"
        headers['Accept'] = "*/*"
        headers['Cookie'] = "JSESSIONID=%s" %self.jsession
        
        if scheme == 'https' :
            connection = httplib.HTTPSConnection(netloc, timeout=100, context=self.ssl_context)
        else :
            connection = httplib.HTTPConnection(netloc, timeout=100)
        
        if options != None :
            path += '?%s' % options
        connection.request('GET', path, "", headers)
            
        response = connection.getresponse()
        if response.status != 200 :
            connection.close()
            raise XNATException('HTTP response: #%s - %s' % (response.status, response.reason))
        
        responseOutput = response.read()
        connection.close()
        
        jsonOutput = json.loads(responseOutput)
        resultSet = jsonOutput['ResultSet']['Result']
        
        return resultSet, response    
        
    def postURL(self, URL, options=None):
        '''Updates an XNAT REST resource'''
        
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(URL)
        
        headers = {}
        headers['Content-type'] = "application/x-www-form-urlencoded"
        headers['Accept'] = "*/*"
        headers['Cookie'] = "JSESSIONID=%s" %self.jsession
        
        if scheme == 'https' :
            connection = httplib.HTTPSConnection(netloc, timeout=100, context=self.ssl_context)
        else :
            connection = httplib.HTTPConnection(netloc, timeout=100)
        
        if options != None :
            path += '?%s' % options
        connection.request('POST', path, "", headers)
            
        response = connection.getresponse()
        connection.close()
            
        if response.status != 200 :
            raise XNATException('HTTP response: #%s - %s' % (response.status, response.reason))
            
        return response
        
    def putURL(self, URL, options=None):
        '''Creates an XNAT REST resource with no body data'''
        
        return self.putData(URL, "", options)
        
    def putData(self, URL, data, options=None):
        '''Creates an XNAT REST resource with body data'''
        
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(URL)
        
        headers = {}
        headers['Content-type'] = "application/x-www-form-urlencoded"
        headers['Accept'] = "*/*"
        headers['Cookie'] = "JSESSIONID=%s" %self.jsession
        
        if scheme == 'https' :
            connection = httplib.HTTPSConnection(netloc, timeout=100, context=self.ssl_context)
        else :
            connection = httplib.HTTPConnection(netloc, timeout=100)
        
        if options != None :
            path += '?%s' % options
        connection.request('PUT', path, data, headers)
            
        response = connection.getresponse()        
            
        if response.status not in [201, 200] :
            raise XNATException('HTTP response: #%s - %s' % (response.status, response.reason))
        
        responseOutput = response.read()
        connection.close()
        
        return response,responseOutput
    
    def putFile(self, URL, fileName, options=None):
        '''Creates an XNAT REST resource and uploads file content included as message body'''
        
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(URL)
        
        #Read the file content to include it as message body and compose the content_type header
        content_type, body = self.encodeBodyHTTP(fileName)
        
        headers = {}
        #Content type "application/x-www-form-urlencoded" is inefficient for sending large quantities of binary data
        #The content type "multipart/form-data" should be used for submitting forms that contain files and binary data
        
        headers['Content-type'] = content_type
        headers['Accept'] = "*/*"
        headers['Cookie'] = "JSESSIONID=%s" %self.jsession
        
        if scheme == 'https' :
            connection = httplib.HTTPSConnection(netloc, timeout=100, context=self.ssl_context)
        else :
            connection = httplib.HTTPConnection(netloc, timeout=100)
        
        if options != None :
            path += '?%s' % options
        connection.request('PUT', path, body, headers)
        
        response = connection.getresponse()
        if response.status != 200 :
            connection.close()
            raise XNATException('HTTP response: #%s - %s' % (response.status, response.reason))
            
        connection.close()
        
        return response
    
    def deleteURL(self, URL, options=None):
        '''Delete an XNAT resource'''
        
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(URL)
        
        headers = {}
        headers['Content-type'] = "application/x-www-form-urlencoded"
        headers['Accept'] = "*/*"
        headers['Cookie'] = "JSESSIONID=%s" %self.jsession
        
        if scheme == 'https' :
            connection = httplib.HTTPSConnection(netloc, timeout=3600, context=self.ssl_context)
        else :
            connection = httplib.HTTPConnection(netloc, timeout=3600)
        
        if options != None :
            path += '?%s' % options
        connection.request('DELETE', path, "", headers)
            
        response = connection.getresponse()
        connection.close()
            
        if response.status != 200 :
            raise XNATException('HTTP response: #%s - %s' % (response.status, response.reason))
            
        return response
    
    def encodeBodyHTTP(self, file_path):
        '''Encode a file as part of a multipart/form-data HTTP message to be uploaded'''
        '''Returns the Body and the Content-type of the HTTP request properly formed'''    
        
        BOUNDARY = '------boundary------'
        CRLF = '\r\n'
        body = []
        
        # UNIX-related issue: CRLF.join "UnicodeDecodeError: 'ascii' codec can't decode byte 0xa0 in position"
        if isinstance(file_path, unicode) :
            file_path = (file_path).encode('utf8')
        file_name = os.path.basename(file_path)
        file_content = self.loadFile(file_path)
        
        body.extend(
          ['--' + BOUNDARY,
           'Content-Disposition: form-data; name="file"; filename="%s"' % file_name,
           # The upload server determines the mime-type, no need to set it.
           'Content-Type: application/octet-stream',
           '',
           file_content,
           ])
        # Finalize the form body
        body.extend(['--' + BOUNDARY + '--', ''])
        
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
        body = CRLF.join(body)
        
        return content_type, body
    
    def loadFile(self, infile):
        '''Open and reads a locally accessible file and its content'''    
        '''Returns the content of the file'''
            
        try:
            fobj = open(infile, 'rb')
        except IOError:
            raise Exception('Cannot open file ', infile)
            
        else: 
            try: 
                fileContent = fobj.read()
            except Exception:
                raise Exception('%s file cannot be read' %infile)
                
            finally:
                fobj.close()
                
        return fileContent
        
    def getJSessionID(self):
        '''Authenticates and returns a session ID'''
        #compose the URL for the REST call
        URL = self.host + '/data/JSESSION'
        
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(URL)
        
        headers = {}
        headers['Content-type'] = "application/x-www-form-urlencoded"
        headers['Accept'] = "*/*"
        headers['Authorization'] = "Basic %s" % self.b64Auth 
        
        if scheme == 'https' :
            connection = httplib.HTTPSConnection(netloc, timeout=10, context=self.ssl_context)
        else :
            connection = httplib.HTTPConnection(netloc, timeout=10)
        
        connection.request('POST', path, "", headers)
        response = connection.getresponse()
        if response.status != 200 :
            connection.close()
            raise XNATException('HTTP response: #%s - %s' % (response.status, response.reason))
            
        sessionID = response.read()
        connection.close()
        
        return sessionID

    def closeJSessionID(self):
        '''Destroy the session ID'''
        #compose the URL for the REST call
        URL = self.host + '/data/JSESSION'
        
        (scheme, netloc, path, params, query, fragment) = urlparse.urlparse(URL)
            
        headers = {}
        headers['Content-type'] = "application/x-www-form-urlencoded"
        headers['Accept'] = "*/*"
        headers['Cookie'] = "JSESSIONID=%s" %self.jsession 
        
        if scheme == 'https' :
            connection = httplib.HTTPSConnection(netloc, timeout=10, context=self.ssl_context)
        else :
            connection = httplib.HTTPConnection(netloc, timeout=10)
            
        connection.request('DELETE', path, "", headers)
        response = connection.getresponse()
        
        if response.status != 200 :
            connection.close()
            raise XNATException('HTTP response: #%s - %s' % (response.status, response.reason))
        
        connection.close()
        
        return self.jsession
    
    def getProjects(self):
        '''Query XNAT REST interface for project list'''
        '''Returns a dictionary with project IDs, names, description and URIs'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'projects'
        
        #encode query options
        query_options = {}
        query_options['columns'] = 'xnat:projectData/ID,name,xnat:projectData/description'
        query_options = urllib.urlencode(query_options)
                
        #do the HTTP query
        projects,response = self.queryURL(URL,query_options)    
        
        #parse the results    
        projectDict = {}    
        for project in projects:
            projectDict[project['ID']] = project                        
        
        return projectDict        
        
    def getSingleProject(self, projectID):
        '''Query XNAT REST interface for an specific project'''
        '''Returns a dictionary with project IDs, names, description and URIs'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'projects'
        
        #encode query options
        query_options = {}
        query_options['ID'] = projectID
        query_options['columns'] = 'xnat:projectData/ID,name,xnat:projectData/description'
        query_options = urllib.urlencode(query_options)
                
        #do the HTTP query
        projects,response = self.queryURL(URL,query_options)    
    
        #parse the results    
        projectDict = {}    
        for project in projects:
            projectDict[project['ID']] = project['URI']
        
        return projectDict
        
    def getProjectUsers(self,project):
        '''Query for users list/roles given a project'''
        '''Returns a dictionary with users having access to such Project'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'projects/%s/users' %project
        
        #do the HTTP query
        projectUsers,response = self.queryURL(URL)    
        
        #parse the results    
        projectUsersDict = {}    
        for projectUser in projectUsers:
            projectUsersDict[projectUser['login']] = projectUser
        
        return projectUsersDict
    
    def getProjectPipelines(self,project):
        '''Query for available pipelines given a project'''
        '''Returns a dictionary with pipelines in such Project'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'projects/%s/pipelines' %project
        
        #do the HTTP query
        pipelines,response = self.queryURL(URL)    
        
        #parse the results    
        projectPipelinesDict = {}    
        for pipeline in pipelines:
            projectPipelinesDict[pipeline['Name']] = pipeline
        
        return projectPipelinesDict
        
    def getSubjects(self, project=None, options=None):
        '''Query for subjects list given a project'''
        '''Returns a dictionary with subjects included in such Project'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        if project == None :
            URL += 'subjects'
        else: 
            URL += 'projects/%s/subjects' %project
            
        #do the HTTP query
        if options != None :
            options_encoded = urllib.urlencode(options)
            resultSet,response = self.queryURL(URL,options_encoded)    
        else: 
            resultSet,response = self.queryURL(URL)    
        
        #parse the results    
        subjectDict = {}    
        for record in resultSet:
            subjectDict[record['ID']] = record
        
        return subjectDict
        
    def getMRSessionsBySubj(self, project, subject, options=None):
        '''Query for MRI sessions list given a subject'''
        '''Returns a dictionary with MRI experiments included in such Subject'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'projects/%s/subjects/%s/experiments' %(project, subject)
        
        if options == None :
            options = { 'xsiType': 'xnat:mrSessionData' }            
            options_encoded = urllib.urlencode(options)
        else:
            options_encoded = urllib.urlencode(options)
        
        #do the HTTP query
        resultSet,response = self.queryURL(URL,options_encoded)            
        
        #parse the results    
        mrDict = {}    
        for record in resultSet :
            #mrDict[record['ID']] = record['label']        
            mrDict[record['ID']] = record
        
        return mrDict
    
    def getMRSessions(self, project, options=None):
        '''Query for MRI session list given a project'''
        '''Returns a dictionary with MRI experiments'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'projects/%s/experiments' %project
        
        if options == None :
            options = { 'xsiType': 'xnat:mrSessionData' }            
            options_encoded = urllib.urlencode(options)
        else:
            options_encoded = urllib.urlencode(options)
            
        #do the HTTP query
        resultSet,response = self.queryURL(URL, options_encoded)    
        
        #parse the results    
        mrDict = {}    
        for record in resultSet :
            #mrDict[record['ID']] = record['label']        
            mrDict[record['ID']] = record
        
        return mrDict
        
    def getScans(self, experimentID, options=None):
        '''Query for scan list given an MRI session'''
        '''Returns a dictionary with scans found in such MRI session'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'experiments/%s/scans' %experimentID
        
        if options != None :
            options_encoded = urllib.urlencode(options)
            resultSet,response = self.queryURL(URL,options_encoded)    
        else: 
            resultSet,response = self.queryURL(URL)    
        
        #parse the results    
        scanDict = {}    
        for record in resultSet :
            #scanDict[record['ID']] = record['type']        
            scanDict[record['ID']] = record
        
        return scanDict
        
    def getResources(self, experimentID, options=None):
        '''Query for ALL scan's resource collections given an MRI Session'''
        '''Returns a dictionary with all resource collections archived per such MRI Session'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'experiments/%s/scans/ALL/resources' %experimentID
        
        if options != None :
            options_encoded = urllib.urlencode(options)
            resultSet,response = self.queryURL(URL,options_encoded)    
        else: 
            resultSet,response = self.queryURL(URL)    
            
        #parse the results    
        resourceDict = {}    
        for record in resultSet :
            #resourceDict[record['label']] = record <-- label might not be unique (i.e. several scans with same resource type/name)
            resourceDict[record['xnat_abstractresource_id']] = record        
        return resourceDict
    
    def getResourcesByScan(self, experimentID, scanID, options=None):
        '''Query for scan resource collections given an MRI Session and a scan'''
        '''Returns a dictionary with all resource collections archived per such scan'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'experiments/%s/scans/%s/resources' %(experimentID,scanID)
        
        if options != None :
            options_encoded = urllib.urlencode(options)
            resultSet,response = self.queryURL(URL,options_encoded)    
        else: 
            resultSet,response = self.queryURL(URL)    
            
        #parse the results    
        resourceDict = {}    
        for record in resultSet :
            #resourceDict[record['label']] = record <-- label might not be unique (i.e. several scans with same resource type/name)
            resourceDict[record['xnat_abstractresource_id']] = record        
        return resourceDict

    def getDerivedResources(self, experimentID):
        '''Query for derived data resources list given an experiment'''
        '''Returns a dictionary with the derived data resources existing for such experiment or None otherwise'''

        # compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'experiments/%s/resources' % experimentID

        # do the HTTP query
        resultSet, response = self.queryURL(URL)

        # an MRI Session can perfectly have no reconstructions!
        resource_dict = {}
        if len(resultSet) != 0:
            # parse the results
            for record in resultSet:
                resource_dict[record['xnat_abstractresource_id']] = record
        else:
            resource_dict = None

        return resource_dict

    def getReconstructions(self, experimentID):
        '''Query for reconstructions list given an experiment'''
        '''Returns a dictionary with the reconstructions created for such experiment or None otherwise'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'experiments/%s/reconstructions' %experimentID
        
        #do the HTTP query
        resultSet,response = self.queryURL(URL)    
        
        #an MRI Session can perfectly have no reconstructions!
        reconstructionDict = {}    
        if len(resultSet) != 0 :         
            #parse the results            
            for record in resultSet :
                reconstructionDict[record['ID']] = record        
        else :
            reconstructionDict = None
        
        return reconstructionDict
        
    def getOutputResources(self, experimentID,reconstructionID):
        '''Query for derived data resource collections of a reconstruction event'''
        '''Returns a dictionary with all resource collections per such reconstruction'''
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'experiments/%s/reconstructions/%s/out/resources' %(experimentID, reconstructionID)
        
        #do the HTTP query
        resultSet,response = self.queryURL(URL)    
        
        #parse the results    
        resourceDict = {}    
        for record in resultSet :
            resourceDict[record['xnat_abstractresource_id']] = record
        return resourceDict
    
    def addSubject(self,projectID,subjectName):
        '''Check if viable and add a Subject resource to XNAT'''
        '''Returns a HTTPlib response structure and the subject unique ID (XNAT accession number)'''    
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'projects/'
        URL += projectID
        projURL = URL
        URL += '/subjects/'
        URL += subjectName
        
        # Check if project exists and connectivity is available
        if self.resourceExist(projURL).status != 200 :
            raise XNATException('XNAT Project %s is unreachable at: %s' % (projectID, projURL) )
        # Check if subject already existed
        elif self.resourceExist(URL).status == 200 :
            raise XNATException('A Subject with such name (%s) already exists within the current context' %subjectName)

        #Otherwise, lets create it    
        response,subjUID = self.putURL(URL)
        #subjUID = response.read()
        
        if self.verbose : print '[Debug] HTTP response: #%s - %s' % (response.status, response.reason)
        return response,subjUID

    def addSession(self,projectID, subjectName, sessionName, options=None):
        '''Check if viable and add a Session resource to XNAT'''
        '''Returns a HTTPlib response structure and the session unique ID (XNAT accession number)'''    
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'projects/'
        URL += projectID
        projURL = URL
        URL += '/subjects/'
        URL += subjectName
        subjURL = URL
        URL += '/experiments/'
        URL += sessionName
        
        # Check if project exists and connectivity is available
        if self.resourceExist(projURL).status != 200 :
            raise XNATException('XNAT Project %s is unreachable at: %s' % (projectID, projURL) )
        # Check if subject exists and connectivity is available
        if self.resourceExist(subjURL).status != 200 :
            raise XNATException('XNAT Subject %s is unreachable at: %s' % (subjectName, subjURL) )
        # Check if session already existed
        elif self.resourceExist(URL).status == 200 :
            raise XNATException('A Session with such name (%s) already exists within the current context' %sessionName)

        #Convert the options to an encoded string suitable for the HTTP request
        encodedOpts = urllib.urlencode(options)    
        
        #Otherwise, lets create it    
        response,sessionUID = self.putURL(URL,encodedOpts)
        #sessionUID = response.read()
        
        if self.verbose : print '[Debug] HTTP response: #%s - %s' % (response.status, response.reason)
        return response,sessionUID
        
    def addScan(self,projectID, subjectName, sessionName, scanID, options=None):
        '''Check if viable and add a Scan resource to XNAT'''
        '''Returns a HTTPlib response structure'''    
        
        #compose the URL for the REST call
        URL = self.host + '/data/'
        URL += 'projects/'
        URL += projectID
        projURL = URL
        URL += '/subjects/'
        URL += subjectName
        subjURL = URL
        URL += '/experiments/'
        URL += sessionName
        sessURL = URL
        URL += '/scans/'
        URL += scanID
        
        # Check if project exists and connectivity is available
        if self.resourceExist(projURL).status != 200 :
            raise XNATException('XNAT Project %s is unreachable at: %s' % (projectID, projURL) )
        # Check if subject exists and connectivity is available
        if self.resourceExist(subjURL).status != 200 :
            raise XNATException('XNAT Subject %s is unreachable at: %s' % (subjectName, subjURL) )
        # Check if session exists and connectivity is available
        if self.resourceExist(sessURL).status != 200 :
            raise XNATException('XNAT Session %s is unreachable at: %s' % (subjectName, sessURL) )
        # Check if scan already existed
        elif self.resourceExist(URL).status == 200 :
            raise XNATException('A Scan with such name (%s) already exists within the current context' %scanID)

        #Convert the options to an encoded string suitable for the HTTP request
        encodedOpts = urllib.urlencode(options)    
        
        #Otherwise, lets create it    
        response,scanUID = self.putURL(URL,encodedOpts)
        
        if self.verbose : print '[Debug] HTTP response: #%s - %s' % (response.status, response.reason)
        return response
        
    
    def launchPipeline(self, projectID, experimentID, pipelineID, params=None):
        '''Launches a pipeline for a specific experiment, can get a list of properly parsed input params'''
        '''Returns a HTTPlib response structure'''    
        
        #compose the URL for the REST call
        URL = self.host + '/data/archive/projects/%s/' % projectID
        URL += 'pipelines/%s/' % pipelineID
        URL += 'experiments/%s' % experimentID
        
        response = self.postURL(URL,params)
        
        if self.verbose : 
            print '[Info] Pipeline %s triggered for experiment %s: #%s - %s (%s)' % (pipelineID, experimentID, response.status, response.reason, datetime.datetime.now())
        
        return response