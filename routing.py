
class ClusterDistribution(object):

    def __init__(self, nb_hosts, current_host=0):

        self.nb_clusters = 256
        self.nb_hosts = nb_hosts
        self.clusters_by_host = self.nb_clusters / self.nb_hosts
        # index of the current host
        self.current_host = current_host
        self.distribution = self.generate_distribution()

    def get_host_from_cluster(self, cluster_index):
        """Say on which server the cluster should be."""
        position = self.distribution.index(cluster_index)
        return position / self.clusters_by_host

    def clusters_for_host(self, host_index):
        """Return the host clusters."""
        slice_size = float(nb_clusters) / self.nb_hosts
        start_slice = int(host_index * slice_size)
        end_slice = int((host_index+1) * slice_size)
        return self.distribution[start_slice:end_slice]

    def generate_distribution(self):
        """According to the number of hosts, this function
        return an array clusters (number) in the order
        they should be stored on the servers.

        Every time a host is added to the pool, a number
        of clusters should moved to the new host. This distribution
        algorithm minimise the number of cluster that needs to be
        moved after every new host has been added to the pool.

        2 servers
        s1            s2
        0 1 2 3 4 5   6 8 9 10 11     <--- clusters

        3 servers
        s1        s2         s3
        0 1 2 3   6 7 8 9   4 5 10 11

        4 servers
        s1      s2      s3       s4
        0 1 2   6 7 8   4 5 10   3 9 11
        """
        clusters = range(0, self.nb_clusters)

        nb = 2
        while nb < self.nb_hosts:
            slice_before = self.nb_clusters / nb
            slice_now = self.nb_clusters / (nb + 1)
            need_to_take = slice_now / nb

            for s in range(nb):
                pos = ((s + 1) * slice_before) - (need_to_take * (s + 1))
                for n in range(need_to_take):
                    moved_cluster = clusters.pop(pos)
                    clusters.append(moved_cluster)

            nb += 1

        return clusters