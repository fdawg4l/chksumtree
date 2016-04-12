# chksumtree

If you're paranoid about bitrot on files you don't access often, this utility will keep track of a given path and let you know when files have changed outside of modification.

```
 python ~/src/python/chksumtree/chksumtree.py --data=./.chksumdat -p .
<Values at 0x10a583e60: {'data_file': './.chksumdat', 'path': '.', 'dryrun': False, 'verbose': False, 'read_buffer': 8192}>
Dat file found successfully
.chksumdat was added.
...
```

If a file was modified, the checksum for it is updated.  If a file was added, it's current chekcsum and fileinfo are added to the dat file.  If a file's checksum has changed but the fileinfo hasn't, time to start freaking out.

```
# For example
Traceback (most recent call last):
  File "/Users/fahmed/src/python/chksumtree/chksumtree.py", line 227, in <module>
    main()
  File "/Users/fahmed/src/python/chksumtree/chksumtree.py", line 222, in main
    chksums.compute(options)
  File "/Users/fahmed/src/python/chksumtree/chksumtree.py", line 137, in compute
    self._checkfile(in_file, options)
  File "/Users/fahmed/src/python/chksumtree/chksumtree.py", line 185, in _checkfile
    in_file_cksum['md5']))
Exception: Mp3s/terrible_song_from_the_90s.mp3 changed from 68rfa3bcc1406510d209dad55ae5d93d to 79df2693128e8442fc121fd727eaba31
```
