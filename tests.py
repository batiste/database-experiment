import unittest
from routing import ClusterDistribution
from hosts import get_pool_request, register_pool_request, join_pool_request
import urllib2
import cjson

class TestServers(unittest.TestCase):

    servers = []

    def setUp(self):
        import shlex, subprocess
        import time
        
        args = shlex.split('python server.py -p8080')
        server1 = subprocess.Popen(args)
        self.servers.append(server1)

        args = shlex.split('python server.py -p8081')
        server2 = subprocess.Popen(args)
        self.servers.append(server2)

        args = shlex.split('python server.py -p8082')
        server2 = subprocess.Popen(args)
        self.servers.append(server2)
        
        time.sleep(0.5)

        
    def test_get_pool(self):

        req = get_pool_request('127.0.0.1:8080')
        data = urllib2.urlopen(req)
        self.assertEqual(
            cjson.decode(data.read()),
            [{"index": 0, "state": "alone", "address": "127.0.1.1:8080"}]
        )

        req = get_pool_request('127.0.0.1:8081')
        data = urllib2.urlopen(req)
        self.assertEqual(
            cjson.decode(data.read()),
            [{"index": 0, "state": "alone", "address": "127.0.1.1:8081"}]
        )

    def test_join_pool(self):

        req = join_pool_request('127.0.1.1:8080', '127.0.1.1:8081')
        data = urllib2.urlopen(req)
        self.assertEqual(
            cjson.decode(data.read()),
            [
                {"index": 0, "state": "pooling", "address": "127.0.1.1:8081"},
                {"index": 1, "state": "pooling", "address": "127.0.1.1:8080"}
            ]
        )

        req = get_pool_request('127.0.0.1:8081')
        data = urllib2.urlopen(req)
        self.assertEqual(
            cjson.decode(data.read()),
            [
                {"index": 0, "state": "pooling", "address": "127.0.1.1:8081"},
                {"index": 1, "state": "pooling", "address": "127.0.1.1:8080"}
            ]
        )
        
        req = get_pool_request('127.0.0.1:8080')
        data = urllib2.urlopen(req)
        self.assertEqual(
            cjson.decode(data.read()),
            [
                {"index": 0, "state": "pooling", "address": "127.0.1.1:8081"},
                {"index": 1, "state": "pooling", "address": "127.0.1.1:8080"}
            ]
        )


        req = join_pool_request('127.0.1.1:8082', '127.0.1.1:8081')
        data = urllib2.urlopen(req)
        self.assertEqual(
            cjson.decode(data.read()),
            [
                {"index": 0, "state": "pooling", "address": "127.0.1.1:8081"},
                {"index": 1, "state": "pooling", "address": "127.0.1.1:8080"},
                {"index": 2, "state": "pooling", "address": "127.0.1.1:8082"}
            ]
        )

        #[{'index': 1, 'state': 'pooling', 'address': '127.0.1.1:8080'},
        #{'index': 0, 'state': 'pooling', 'address': '127.0.1.1:8081'},
        #{'index': 1, 'state': 'pooling', 'address': '127.0.1.1:8080'},
        #{'index': 2, 'state': 'pooling', 'address': '127.0.1.1:8082'}]


    def tearDown(self):
        for server in self.servers:
            server.kill()


class TestDistribution(unittest.TestCase):

    def test_distribution(self):
        distrib = ClusterDistribution(1, nb_clusters=12)
        self.assertEqual(
            distrib.distribution,
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        )
        distrib = ClusterDistribution(2, nb_clusters=12)
        self.assertEqual(
            distrib.distribution,
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        )
        distrib = ClusterDistribution(3, nb_clusters=12)
        self.assertEqual(
            distrib.distribution,
            [0, 1, 2, 3, 6, 7, 8, 9, 4, 5, 10, 11]
        )
        distrib = ClusterDistribution(4, nb_clusters=12)
        self.assertEqual(
            distrib.distribution,
            [0, 1, 2, 6, 7, 8, 4, 5, 10, 3, 9, 11]
        )
        self.assertEqual(
            distrib.clusters_for_host(0),
            [0, 1, 2]
        )
        self.assertEqual(
            distrib.clusters_for_host(3),
            [3, 9, 11]
        )
        self.assertEqual(
            distrib.get_host_from_cluster(3),
            3
        )
        self.assertEqual(
            distrib.get_host_from_cluster(11),
            3
        )
        self.assertEqual(
            distrib.get_host_from_cluster(2),
            0
        )



if __name__ == '__main__':
    unittest.main()