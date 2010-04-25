==========================================
A python database that partition itself
==========================================

This project is a experiment that implement
a very simple json data store that can partition the
data accross several servers in a totally automatic way.

The idea is to have a pool of servers. You can add servers to your
pool and some data will be automaticaly migrated from the old
servers to the new one to equalize the load.

This experiment currently uses 256 clusters of data. Every json data is assigned to a cluster
using the first 2 characters of the index (a md5 hexadecimal hash).

* An algorithm is used to determine to which server everyone of these clusters should go.
* Every server get the same amount of of clusters.
* Everytime a server is added to the pool the clusters are redistributed.
* The redistribution is designed to move the smallest amount of clusters
  and to move the same amount from every server.

Todo
======

* Save pool configuration on disk.
* Implement a way to move clusters or/and documents (automatic or on demand?).
* Implement a client library.
* Tests.
* Save documents in cluster directories.
* ...


