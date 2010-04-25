=========================================
A python database that partition itself
==========================================

This project is a experiment in trying to implement
a very simple json data store that can partition the
data in a totally automatic way.

The idea is to have a pool of servers. You can add servers to your
pool and some data will be automaticaly migrated from the old
servers to the new one to equalize the load.

