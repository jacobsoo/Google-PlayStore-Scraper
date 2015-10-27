import urllib2
import urllib
import re


class Request:
    def __init__(self, tries):
        self.header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}
        self.data = None
        self._tries = tries

    def _getUrl(self):
        raise NotImplementedError

    def _success(self):
        pass

    def _error(self):
        pass

    def download(self, successCallback=lambda obj:{}, errorCallback=lambda obj,e:{}):
        if self.data is not None:
            raise Exception("already executed")
        req = urllib2.Request(self._getUrl(), None, self.header)
        try:
            response = urllib2.urlopen(req)
            self.data = response.read()
        ## TODO only catch specific exception, implement retry for recoverable exceptions
        except Exception as e:
            self._error()
            errorCallback(self, e)
            raise e
        else:
            self._success()
            successCallback(self)


    def _getResult(self):
        return self.data

    def getApps(self):
        return []

    def getRequests(self):
        return []

    def toDict(self):
        raise NotImplementedError

    def incTries(self):
        self._tries += 1

    def getTries(self):
        return self._tries

    def __eq_(self, other):
        if type(other) is type(self):
            return self._getUrl() == other._getUrl()
        return False

    def __repr__(self):
        return self.__class__.__name__+'(%s)'%self._getUrl()


class CategoryRequest(Request):
    appParser = re.compile('class="preview-overlay-container" data-docid="(.+?)"')
    developerParser = re.compile('href="/store/apps/developer\?id=([^"]+)"')

    def __init__(self, category, collection, tries=0):
        Request.__init__(self, tries)
        self.category = category
        self.collection = collection
        self._apps = []
        self._dev = []


    def _getUrl(self):
        return 'https://play.google.com/store/apps/category/%s/collection/%s?authuser=0' % (urllib.quote(self.category), urllib.quote(self.collection))

    def _success(self):
        ## parse page, extract apps
        self._apps = set(CategoryRequest.appParser.findall(self.data))
        self._dev = set(CategoryRequest.developerParser.findall(self.data))

    def getApps(self):
        return self._apps

    def getRequests(self):
        return map(AppRequest, self._apps) + map(DeveloperRequest, self._dev)

    def toDict(self):
        return {'type': self.__class__.__name__, 'category': self.category, 'collection': self.collection, 'tries': self.getTries()}

    @staticmethod
    def fromDict(obj):
        if not type(obj) is dict or not obj['type'] == CategoryRequest.__name__:
            raise ValueError('invalid data')
        if 'category' not in obj or 'collection' not in obj or 'tries' not in obj:
            raise ValueError('invalid data')
        return CategoryRequest(obj['category'], obj['collection'], obj['tries'])

    def __eq__(self, other):
        if type(other) is type(self):
            return self.category == other.category and self.collection == other.collection
        return False

    def __repr__(self):
        return self.__class__.__name__+'("%s", "%s")' % (self.category, self.collection)


class DeveloperRequest(Request):
    def __init__(self, developer, tries=0):
        Request.__init__(self, tries)
        self._tries = 0
        self.developer = developer
        self._apps = []

    def _getUrl(self):
        return 'https://play.google.com/store/apps/developer?id=%s' % urllib.quote(self.developer)

    def _success(self):
        ## parse
        pass

    def getApps(self):
        return self._apps

    def getRequests(self):
        return map(AppRequest, self._apps)

    def toDict(self):
        return {'type': self.__class__.__name__, 'developer': self.developer, 'tries': self.getTries()}

    @staticmethod
    def fromDict(obj):
        if not type(obj) is dict or not obj['type'] == DeveloperRequest.__name__:
            raise ValueError('invalid data')
        if 'developer' not in obj or 'tries' not in obj:
            raise ValueError('invalid data')
        return DeveloperRequest(obj['developer'])

    def __eq__(self, other):
        if type(other) is type(self):
            return self.developer == other.developer
        return False

    def __repr__(self):
        return self.__class__.__name__+'("%s")' % self.developer


class AppRequest(Request):
    def __init__(self, pkgname, tries=0):
        Request.__init__(self, tries)
        self.pkgname = pkgname
        self._apps = []
    
    def _getUrl(self):
        return 'https://play.google.com/store/apps/details?id=%s' % urllib.quote(self.pkgname)

    def _success(self):
        ## parse similar apps
        pass

    def getApps(self):
        return self._apps

    def getRequests(self):
        return map(AppRequest, self._apps)

    def toDict(self):
        return {'type': self.__class__.__name__, 'pkgname': self.pkgname, 'tries': self.getTries()}

    @staticmethod
    def fromDict(obj):
        if not type(obj) is dict or not obj['type'] == AppRequest.__name__:
            raise ValueError('invalid data')
        if 'pkgname' not in obj or 'tries' not in obj:
            raise ValueError('invalid data')
        return AppRequest(obj['pkgname'])
    
    def __eq__(self, other):
        if type(other) is type(self):
            return self.pkgname == other.pkgname
        return False

    def __repr__(self):
        return self.__class__.__name__+'("%s")' % self.pkgname