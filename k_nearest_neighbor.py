import heapq
import multiprocessing
import sys

class Dist2:
    def __init__(self, nodes):
        self._nodes = nodes

    def __call__(self, index1, index2):
        node1 = self._nodes[index1]
        node2 = self._nodes[index2]
        return ((node1[0] - node2[0]) ** 2) + ((node1[1] - node2[1]) ** 2)

def read_nodes(filename):
    return list(map(lambda line: tuple(map(int, line.split(','))),
                    open(filename)))

class NearestNeighbors:
    def __init__(self, k, num_nodes, dist):
        self._k = k
        self._num_nodes = num_nodes
        self._dist = dist

    def __call__(self, index):
        k_nearest = heapq.nsmallest(
            self._k + 1, 
            map(lambda other_index: (self._dist(index, other_index),
                                     other_index),
                range(self._num_nodes)))

        return list(map(lambda pair: pair[1], k_nearest[1:]))

# Parameters:
#   - number of processes
#   - k
#   - instance
def main():
    num_procs = int(sys.argv[1])
    k = int(sys.argv[2])
    nodes = read_nodes(sys.argv[3])
    dist2 = Dist2(nodes)
    num_nodes = len(nodes)

    pool = multiprocessing.Pool(processes=num_procs)

    for neighbors in pool.map(NearestNeighbors(k, num_nodes, dist2), 
                              range(num_nodes)):
        print(','.join(map(str, neighbors)))

if __name__ == '__main__':
    main()

