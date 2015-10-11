import urllib2
import urllib
import re, argparse, time
from bs4 import BeautifulSoup
import codecs

szCategories = ['BOOKS_AND_REFERENCE','BUSINESS',
                'COMICS','COMMUNICATION',
                'EDUCATION','ENTERTAINMENT',
                'FINANCE','HEALTH_AND_FITNESS',
                'LIBRARIES_AND_DEMO','LIFESTYLE',
                'APP_WALLPAPER','MEDIA_AND_VIDEO',
                'MEDICAL','MUSIC_AND_AUDIO',
                'NEWS_AND_MAGAZINES','PERSONALIZATION',
                'PHOTOGRAPHY','PRODUCTIVITY',
                'SHOPPING','SOCIAL',
                'SPORTS','TOOLS',
                'TRANSPORTATION','TRAVEL_AND_LOCAL',
                'WEATHER','APP_WIDGETS',
                'GAME_ACTION','GAME_ADVENTURE',
                'GAME_ARCADE','GAME_BOARD',
                'GAME_CARD','GAME_CASINO',
                'GAME_CASUAL','GAME_EDUCATIONAL',
                'GAME_MUSIC',
                'GAME_PUZZLE','GAME_RACING',
                'GAME_ROLE_PLAYING','GAME_SIMULATION',
                'GAME_SPORTS','GAME_STRATEGY',
                'GAME_TRIVIA','GAME_WORD',
                'FAMILY_BRAINGAMES','FAMILY_CREATE',
                'FAMILY_EDUCATION','FAMILY_MUSICVIDEO',
                'FAMILY_PRETEND']

szCollection = ['topselling_free',
                'topselling_paid',
                'topselling_new_free',
                'topselling_new_paid',
                'topgrossing',
                'movers_shakers']
                    
def CurlReq(szOutFile, Category, Collection, index):
    # our parameters
    params = {'start':index,
              'num':'60',
              'numChildren':'0',
              'ipf':'1',
              'xhr':'1' }

    # establish connection with the webpage
    url = 'https://play.google.com/store/apps/category/' + Category + '/collection/' + Collection + '?authuser=0'

    # url encode the parameters
    url_params = urllib.urlencode(params)

    try:
        # send out the POST request
        h = urllib2.urlopen(url, url_params)
        # get the response
        resp = h.read()
        
        # Search for class="preview-overlay-container" data-docid=
        _download_links = re.findall('class="preview-overlay-container" data-docid="(.+?)"', resp, re.DOTALL|re.UNICODE)
        with open(szOutFile, 'ab') as fw:
            for link in _download_links:
                path = 'https://play.google.com/store/apps/details?id=' + link + '\n'
                fw.write(path)
                '''
                The following is used for getting more information about each application
                tmp = 'https://play.google.com/store/apps/details?id=' + link
                hLink = urllib2.urlopen(tmp)
                print('[+] Fetching from %s' % tmp)
                # get the response
                resp2 = hLink.read()
                _title = re.search('class="document-title" itemprop="name"> <div>(.+?)</div>', resp2, re.DOTALL|re.UNICODE)
                print('    [*] Title : %s' % _title.group(1))
                _author = re.search('<span itemprop="name">(.+?)</span>', resp2, re.DOTALL|re.UNICODE)
                print('    [*] Author : %s' % _author.group(1))
                _author_url = re.search('<a class="document-subtitle primary" href="(.+?)"', resp2, re.DOTALL|re.UNICODE)
                print('    [*] Author URL : https://play.google.com%s' % _author_url.group(1))
                _dateUpdated = re.search('<div class="content" itemprop="datePublished">(.+?)</div>', resp2, re.DOTALL|re.UNICODE)
                print('    [*] Date Updated : %s' % _dateUpdated.group(1))
                _filesize = re.search('<div class="content" itemprop="fileSize">(.+?)</div>', resp2, re.DOTALL|re.UNICODE)
                print('    [*] FileSize : %s' % _filesize.group(1))
                _numInstalls = re.search('<div class="content" itemprop="numDownloads">(.+?)</div>', resp2, re.DOTALL|re.UNICODE)
                print('    [*] Number of Installs : %s' % _numInstalls.group(1))
                '''
                '''
                or do a HTTP POST to https://play.google.com/store/xhr/getdoc?authuser=0
                with the following parameters
                ids=com.dictionary&xhr=1
                
                url2 = 'https://play.google.com/store/xhr/getdoc?authuser=0'
                params2 = { 'id':link,
                            'xhr':'1'
                          }
                url_params2 = urllib.urlencode(params2)
                h2 = urllib2.urlopen(url2, url_params2)
                resp2 = h2.read()
                soup = BeautifulSoup(resp, "html.parser")
                title = soup.find('a',{'class':'title'})
                print("Title: %s - https://play.google.com%s" % (title['title'], title['href']))
                dev = soup.find('a',class_='subtitle')
                print("Developer: %s - http://play.google.com%s" % (dev.string, dev['href']))
                hFile = codecs.open('log.txt', 'wb',encoding='utf-8')
                hFile.write(soup.prettify())
                hFile.close()
                '''
        h.close()
    except urllib2.HTTPError:
        pass

def main():
    parser = argparse.ArgumentParser(description='This is a simple Google PlayStore scraper.')
    parser.add_argument('-o','--output',help='-o <output_filename>', required=True)
    args = parser.parse_args()
    
    while True:
        try:
            for category in szCategories:
                for Collection in szCollection:
                    for index in xrange(0,1800,60):
                        CurlReq(args.output, category, Collection, index)
        except KeyboardInterrupt:
            print('\nPausing...  (Hit ENTER to continue, type quit to exit.)')
            try:
                response = raw_input()
                if response == 'quit':
                    break
                print('Resuming...')
            except KeyboardInterrupt:
                print('Resuming...')
                continue

if __name__ == "__main__":
    main()