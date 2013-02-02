import io
import itertools
import math
import os.path
import random
import subprocess
import sys
import tempfile

def Dist(nodes, round_method):
    num_nodes = len(nodes)

    def dist(index1, index2):
        # Dummy node
        if index1 == num_nodes or index2 == num_nodes:
            return 0

        node1 = nodes[index1]
        node2 = nodes[index2]
        return round_method(((node1[0] - node2[0]) ** 2) + \
                                ((node1[1] - node2[1]) ** 2))

    return memoize(dist)

def Linkern(linkern_path, working_dir, num_nodes, dist):
    def create_data_content(num_nodes, dist, edges):
        content = io.StringIO()

        print(num_nodes, len(edges), file=content)

        for edge in edges:
            print(edge[0], edge[1], dist(edge[0], edge[1]), file=content)

        return content.getvalue()

    def create_starting_cycle_content(cycle):
        content = io.StringIO()
        print(len(cycle), file=content)
        print(' '.join(map(str, cycle)), file=content)
        return content.getvalue()

    def linkern(edges, starting_path, time):
        args = [linkern_path, "-N", "10"]
        args.extend(["-o", result_filename])

        # Data
        with open(data_filename, 'w') as file:
            file.write(create_data_content(
                    num_nodes + 1, 
                    dist,
                    list(itertools.chain(edges, null_edges))))
        args.extend(["-g", data_filename])

        # Time
        args.extend(["-t", str(time)])

        # Cycle
        with open(starting_cycle_filename, 'w') as file:
            file.write(create_starting_cycle_content(starting_path \
                                                         + [num_nodes]))
        args.extend(["-y", starting_cycle_filename])

        args.append(data_filename)
                    
        subprocess.call(args, stdout=open(os.devnull, 'w'))

        return cycle2path(read_result(result_filename))

    def read_result(filename):
        with open(filename) as file:
            num_nodes, num_edges = map(int, file.readline().split())

            cycle = list(map(lambda line: int(line.split()[0]), file))
            return cycle


    data_filename = os.path.join(working_dir, "data")
    result_filename = os.path.join(working_dir, "result")
    starting_cycle_filename = os.path.join(working_dir, "cycle")
    null_edges = list(map(lambda i: (i, num_nodes), range(num_nodes)))

    return linkern
    
def cycle2path(cycle):
    dummy_index = len(cycle) - 1
    part1 = [] # before dummy node
    part2 = [] # after dummy node

    found = False

    for node in cycle:
        if node == dummy_index:
            found = True
            continue

        if not found:
            part1.append(node)
        else:
            part2.append(node)

    return part2 + part1

def generate_edges(index, neighbors):
    def generate_edge(neighbor):
        return min(index, neighbor), max(index, neighbor)

    return map(generate_edge, neighbors)

def memoize(fn):
    cache = {}
    def aux(*args):
        value = cache.get(args, None)
        if value is None:
            value = fn(*args)
            cache[args] = value
        return value
    return aux

def path2edges(path):
    def pairwise(iterable):
        "s -> (s0,s1), (s1,s2), (s2, s3), ..."
        a, b = itertools.tee(iterable)
        next(b, None)
        return zip(a, b)

    return map(lambda edge: (min(edge), max(edge)), pairwise(path))

def path_length(dist, edges):
    return sum(map(lambda edge: dist(*edge), edges))

def read_neighbors(filename, k):
    return list(map(lambda line: list(map(int, line.split(',')))[:k],
                    open(filename)))

def read_nodes(filename):
    return list(read_pairs(filename))

def read_pairs(filename):
    return map(lambda line: tuple(map(int, line.split(','))),
               open(filename))

def read_solution(filename):
    return zip(*read_pairs(filename))

def write_solution(filename, path1, path2):
    with open(filename, 'w') as file:
        for pair in zip(path1, path2):
            print(','.join(map(str, pair)), file=file)

# Parameters:
#  - instance
#  - neighbors
#  - initial solution
#  - linkern path
#  - k
#  - path1 time limit
#  - path2 time limit
def main():
    nodes = read_nodes(sys.argv[1])
    k = int(sys.argv[5])
    all_neighbors = read_neighbors(sys.argv[2], 99999)
    path1, path2 = read_solution(sys.argv[3])

    dist_round = Dist(nodes, lambda dist2: round(math.sqrt(dist2)))
    dist = Dist(nodes, lambda dist2: math.sqrt(dist2))
    working_dir = tempfile.mkdtemp()

    with open(os.path.join(working_dir, "parameters"), 'w') as file:
        file.write(' '.join(sys.argv))
        print(file=file)

    linkern = Linkern(sys.argv[4], working_dir, len(nodes), dist_round)

    edges = set(itertools.chain(*map(lambda arg: generate_edges(*arg),
                                     enumerate(all_neighbors))))

    path1_time_limit = int(sys.argv[6])
    path2_time_limit = int(sys.argv[7])

    path1 = list(path1)
    path2 = list(path2)

    while True:
        path1_length = path_length(dist, path2edges(path1))
        path2_length = path_length(dist, path2edges(path2))

        if path1_length < path2_length:
            path1, path2 = path2, path1
            path1_length, path2_length = path2_length, path1_length

        forbidden_edges = list(path2edges(path2))
        random.shuffle(forbidden_edges)

        path1 = linkern(edges - set(forbidden_edges[k:]), path1, 
                        path1_time_limit)
        path2 = linkern(edges - set(path2edges(path1)), path2, path2_time_limit)

        print()
        print("Before")
        print(path1_length)
        print(path2_length)

        print("After")
        print(path_length(dist, path2edges(path1)))
        print(path_length(dist, path2edges(path2)))
        obj_value = int(max(path1_length, path2_length) + 0.5)

        solution_filename = os.path.join(working_dir, str(obj_value))

        if not os.path.exists(solution_filename):
            print("Writing solution to %s" % solution_filename)
            write_solution(solution_filename, path1, path2)

if __name__ == '__main__':
    main()
