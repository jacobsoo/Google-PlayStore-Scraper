from queuelib import FifoDiskQueue
import os

class RequestSet:
    def __init__(self, filename, marshal=lambda x: x, unmarshal=lambda x: x):
        self.marshal = marshal
        self.unmarshal = unmarshal
        if os.path.isfile(filename):
            self._file = open(filename, 'r+')
        else:
            self._file = open(filename, 'w+')
        self._data = self.__load(self._file)

    def contains(self, req):
        return self.marshal(req) in self._data

    def add(self, req):
        rstr = self.marshal(req)
        if rstr in self._data:
            return
        self._data.add(rstr)

        ## write to file
        self._file.seek(0, 2)
        self._file.write(rstr)
        self._file.write('\n')
        self._file.flush()

    def __load(self, fs):
        data = set()
        for line in fs.readlines():
            data.add(line[:-1])
        return data

    def close(self):
        self._file.close()

    def __delete__(self):
        self._file.close()


class RequestQueue(FifoDiskQueue):
    def __init__(self, filename, marshal=lambda x: x, unmarshal=lambda x: x):
        FifoDiskQueue.__init__(self, filename)
        self.marshal = marshal
        self.unmarshal = unmarshal

    
    def push(self, reqt):
        return FifoDiskQueue.push(self, self.marshal(reqt))

    def pop(self):
        return self.unmarshal(FifoDiskQueue.pop(self))

    def __delete__(self):
        self.close()


class AppList:
    def __init__(self, filename):
        if os.path.isfile(filename):
            self._file = open(filename, 'r+')
        else:
            self._file = open(filename, 'w+')

    def add(self, pkgname):
        self._file.seek(0, 2)
        self._file.write(pkgname)
        self._file.write('\n')
        self._file.flush()

    def close(self):
        self._file.close()
        
    def __delete__(self):
        self._file.close()