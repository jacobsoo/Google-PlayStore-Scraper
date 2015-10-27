import os
import argparse
import json
import time
import urllib2

import request
import result












if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This is a simple Google PlayStore scraper.')
    parser.add_argument('-t', help='-t <tmp_foldername>', required=True)
    parser.add_argument('-o', help='-o <output_filename>', required=True)
    args = parser.parse_args()

    marshal = lambda x: json.dumps(x.toDict())
    def unmarshal(jstr):
        if jstr is None:
            return None
        payload = json.loads(jstr)
        for cls in [request.Request, request.CategoryRequest, request.DeveloperRequest, request.AppRequest]:
            if payload['type'] == cls.__name__:
                return cls.fromDict(payload)
        raise ValueError('invalid data')



    todo = result.RequestQueue(os.path.join(args.t, 'todo'), marshal, unmarshal)
    seen = result.RequestSet(os.path.join(args.t, 'seen'), marshal, unmarshal)
    apps = result.AppList(args.o)

    ## seeding
    req = request.CategoryRequest('BUSINESS', 'topselling_free2')
    todo.push(req)

    try:
        ## crawling
        ## TODO move to threads
        next = todo.pop()
        while next is not None:
            ## on exception put back in todo list
            try:
                next.download()
            except Exception as e:
                if next.getTries() == 3:
                    print '%s dropping: %s - %s' % (time.time(), next, str(e))
                else:
                    print '%s retry: %s' % (time.time(), next)
                    next.incTries()
                    todo.push(next)
            else:
                map(apps.add, next.getApps())
                for newRequest in next.getRequests():
                    if not seen.contains(newRequest):
                        todo.push(newRequest)
                        seen.add(newRequest)
                        print '%s queued %s' % (time.time(), newRequest)
            next = todo.pop()
    finally:
        todo.close()
        seen.close()
        apps.close()



