#!/usr/bin/python

import sys
import pickle
import os
import hashlib
import pprint
import time
from optparse import OptionParser

VERSION=1.0


def parseOptions():
    usage = """
            %prog [options]\n 
            Scrub a given directory by calculating the md5 hash of every file and compare
            it with the one stored in the datfile.  If a file's mtime has changed, the md5
            in the datfile will be updated.  If the md5s are different and the mtime hasn't
            changed, an Exception will be raised.  """
    parser = OptionParser(usage=usage)
    parser.add_option("-v", "--verbose",
                        action="store_true",
                        dest="verbose",
                        default=False,
                        help="Verbose output")
    parser.add_option("-n", "--noaction",
                        action="store_true",
                        dest="dryrun",
                        default=False,
                        help="Dry run.  No action will be taken.")
    parser.add_option("-p", "--path",
                        action="store",
                        dest="path",
                        help="Path to walk")
    parser.add_option("-d", "--data",
                        action="store",
                        dest="data_file",
                        default=".chksumdat",
                        help="Data file to store path checksums")
    parser.add_option("-b", "--buffer",
                        action="store",
                        dest="read_buffer",
                        type="int",
                        default="8192",
                        help="Read buffer used when calculating the md5sum in bytes")
    (options, args) = parser.parse_args()
    return options


def md5sum(file, read_buffer):
    ''' Get the md5 of a file '''
    md5 = hashlib.md5()
    f = open(file,'rb') 
    for chunk in iter(lambda: f.read(read_buffer), ''): 
        md5.update(chunk)
    f.close()
    return md5.hexdigest()


def statfile(file):
    return os.stat(file)


class Filedata():
    def __init__(self, options, file, path):
        self.datfile = os.path.join(path, file)
        self._path = path
        self.cksums = {}
        self._read(options)

    def _read(self, options):
        '''
        Read the datfile
        '''
        if os.path.exists(self.datfile):
            print "Dat file found successfully"
            f = open(self.datfile)
            (v, self.cksums) = pickle.load(f)
            f.close()
            if options.verbose: pprint.pprint(self.cksums)

        else:
            #raise Exception("%s does not exist" % self._file)
            print "%s does not exist.  Creating new one." % self.datfile

        if v != VERSION:
            raise Exception("Wrong version.  Please delete %s" % self.datfile)

    def save(self):
        '''
        Save the datfile.
        '''
        f = open(self.datfile, "wa")
        pickle.dump((VERSION, self.cksums), f)
        f.close()

    def compute(self, options):
        '''
        Actually do the work.  Walk the given directory, compute md5s,
        diff it with the known md5, if the mtime is the same and the md5s
        are the same, you're good.  If mtime is different, update the file's
        md5 in the datfile.  GC removed files from the datfile to save space.
        '''

        seen = []
        total_keys = len(self.cksums.keys())
        count = 0

        for (root, dirs, files) in os.walk(self._path):
            for file in files:
                                        # chomp the full path
                if file in [".DS_Store", self.datfile[len(self._path):]]:
                    continue

                in_file = os.path.join(root, file)

                if not os.path.isfile(in_file):
                    continue

                # add it to the files we've seen
                # so we can subtract it from the dict
                # to gc the deleted ones
                seen.append(self._get_rel_path(in_file))

                self._checkfile(in_file, options)
                count = count + 1
                if not options.verbose: self._printprogress(count, total_keys)

        self._gc(seen)

        print "\n"

    def _get_rel_path(self, in_file):

        if in_file.startswith(self._path):
            rel_path = in_file[len(self._path):].lstrip("/")
        else:
            rel_path = in_file.lstrip("/")
        return rel_path

                
    def _checkfile(self, in_file, options):
        '''
        Add new files, check existing files, and update modified files.
        '''

        in_file_cksum = {'stat': os.stat(in_file),
                         'md5':  md5sum(in_file, options.read_buffer)}

        if options.verbose: print in_file

        rel_path = self._get_rel_path(in_file)

        if options.verbose: 
                print rel_path

        f = self.cksums.get(rel_path)

        if f == None:
            # New file.
            print "%s was added." % rel_path
            self.cksums[rel_path] = in_file_cksum

        else:
            # check fi the file was updated
            if (f['stat'].st_mtime == in_file_cksum['stat'].st_mtime):
                
                # stat is the same.  check md5
                if f['md5'] != in_file_cksum['md5']:
                    # Fuck
                    raise Exception("%s changed from %s to %s" % (rel_path,
                                                                  f['md5'],
                                                                  in_file_cksum['md5']))
                else:
                # All good in the hood
                    if options.verbose: print "%s passes md5 %s" % (rel_path, 
                                                                    in_file_cksum['md5'])
            else:
                # file was modified
                print "%s was updated to %s on %s" % (rel_path,
                                                      in_file_cksum['md5'],
                                                      time.ctime(in_file_cksum['stat'].st_mtime))
                self.cksums[rel_path] = in_file_cksum

    def _gc(self, seen):
        '''
        Remove unseen files from datfile
        '''
        for file in (set(self.cksums.keys()) - set(seen)):
            print "%s was deleted" % file
            del self.cksums[file]

    def _printprogress(self, sofar, total):
        if total > 0:
            s = "\t%s/%s Files" % (sofar, total)
        else:
            s = "\t%s Files" % sofar
        sys.stdout.write(s + " " * (78 - len(s)) + "\r")
        sys.stdout.flush()


def main():
    options = parseOptions()
    pprint.pprint(options)
    chksums = Filedata(options,
                       options.data_file,
                       options.path)
                       

    chksums.compute(options)
    if not options.dryrun: chksums.save()


if __name__ == '__main__':
    main()
