import urllib2
import urllib
import re


class Request:
    def __init__(self):
        self.header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36'}
        self.data = None

    def _getUrl(self):
        raise Exception("no implementation")

    def _success(self):
        pass

    def _error(self):
        pass

    def download(self, successCallback=lambda obj:{}, errorCallback=lambda obj,e:{}):
        req = urllib2.Request(self._getUrl(), None, self.header)
        response = urllib2.urlopen(req)
        try:
            self.data = response.read()
        except Exception as e:
            self._error()
            successCallback(self, e)
        else:
            self._success()
            successCallback(self)


    def _getResult(self):
        return self.data

    def getApps(self):
        return []

    def getRequests(self):
        return []

    def __eq_(self, other):
        if type(other) is type(self):
            return self._getUrl() == other._getUrl()
        return False

    def __repr__(self):
        return self.__class__.__name__+'(%s)'%self._getUrl()


class CategoryRequest(Request):
    appParser = re.compile('class="preview-overlay-container" data-docid="(.+?)"')
    developerParser = re.compile('href="/store/apps/developer\?id=([^"]+)"')

    def __init__(self, category, collection):
        Request.__init__(self)
        self.category = category
        self.collection = collection
        self._apps = []
        self._dev = []


    def _getUrl(self):
        return 'https://play.google.com/store/apps/category/%s/collection/%s?authuser=0' % (urllib.quote(self.category), urllib.quote(self.collection))

    def _success(self):
        ## parse page, extract apps
        self._apps = set(CategoryRequest.appParser.findall(self.data))
        dev = set(CategoryRequest.developerParser.findall(self.data))
        self._dev = map(urllib.unquote, dev)


    def getApps(self):
        return self._apps

    def getRequests(self):
        return map(AppRequest, self._apps) + map(DeveloperRequest, self._dev)

    def __eq__(self, other):
        if type(other) is type(self):
            return self.category == other.category and self.collection == other.collection
        return False

    def __repr__(self):
        return self.__class__.__name__+'("%s", "%s")' % (self.category, self.collection)


class DeveloperRequest(Request):
    def __init__(self, developer):
        Request.__init__(self)
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

    def __eq__(self, other):
        if type(other) is type(self):
            return self.developer == other.developer
        return False

    def __repr__(self):
        return self.__class__.__name__+'("%s")' % self.developer


class AppRequest(Request):
    def __init__(self, pkgname):
        Request.__init__(self)
        self.pkgname = pkgname
        self._apps = []
    
    def _getUrl(self):
        return 'https://play.google.com/store/apps/details?id=%s' % urllib(self.pkgname)

    def _success(self):
        ## parse similar apps
        pass

    def getApps(self):
        return self._apps

    def getRequests(self):
        return map(AppRequest, self._apps)
    
    def __eq__(self, other):
        if type(other) is type(self):
            return self.pkgname == other.pkgname
        return False

    def __repr__(self):
        return self.__class__.__name__+'("%s")' % self.pkgname