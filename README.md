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
