# Traveling Santa Problem Solver

This is a heuristic written in Python for the [Traveling Santa
Problem][1]. It is based on [Concorde][2] -- a state-of-the-art
Traveling Salesman Problem (TSP) solver.


## Heuristic

The Traveling Santa Problem naturally decomposes into two TSP with
side constraints (an edge can be in at most one TSP). This heuristic
uses Concorde's Lin-Kernighan heuristic as follows:

1. Run Lin-Kernighan heuristic on first path.  
   Edge restriction: can used at most n edges from the second path.

2. Run Lin-Kernighan heuristic on second path. 
   Edge restriction: can't use any edge from the first path.


## Result

This heuristic (IRO on the [leaderboard][3]) found a solution with an
objective value of 6,593,676, which is at 1% of the solution found by
the winning team (6,526,972).


## Usage

### Computing k Nearest Neighbors

Since each subproblem (TSP) uses a strict subset of the edges, we need
to explicitly list the allowed edges to Concorde. And we can't list
all edges because there are too many (~11 billions). So I decided to
include edges from the k nearest neighbor graph (K-NNG). The script
`k_nearest_neighbor.py` generates such graph in a naive way O(n^2),
but it's fully parallelizable so it shouldn't take too long if you
have a few cores.

Parameters:
  - number of processes
  - k
  - instance

Example:

    python3 k_nearest_neighbor.py 24 200 santa.nodes > santa.neighbors.200

### Running the Heuristic

Parameters:
  - instance
  - neighbors
  - initial solution
  - linkern path
  - k
  - path1 time limit
  - path2 time limit

Example:

    python3 heur.py \
        santa.nodes \
        santa.neighbors.200 \
        incumbent_solution \
        ~/concorde/LINKERN/linkern \
        200 \
        120 \
        300

The script `run` can also be used to launch multiple heur.py in
parallel.

Parameters:
  - number or processes

Example:

    ./run 24

Note: you need to adapt `run` to your environment before using it.

## Author

Mahieu Larose <mathieu@mathieularose.com>


## License

See LICENSE


[1]: http://www.kaggle.com/c/traveling-santa-problem
[2]: http://www.tsp.gatech.edu/concorde.html
[3]: http://www.kaggle.com/c/traveling-santa-problem/leaderboard