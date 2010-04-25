==========================================
A python database that partition itself
==========================================

This project is a experiment that implement
a very simple json data store that can partition the
data accross several servers in a totally automatic way.

The idea is to have a pool of servers. You can add servers to your
pool and some data will be automaticaly migrated from the old
servers to the new one to equalize the load.

There is 256 clusers of data. Every json data is assigned to a cluster
using the first 2 characters of the index (a md5 hexadecimal hash).

Then an algorithm is used to determine on which server of the pool
everyone of these clusters should go. Every server get the same amount
of cluster. Everytime a server is added the clusters are redistributed.
The redistribution is designed to move the smallest amount of cluster.
and to move the same amount from every server.

