# Investigation of a HNSW graphs

The implementations of [hnsw.py](./src/hnsw.py) and other pieces of codes were borrowed from the [repository](https://github.com/aponom84/navigable-graphs-python/tree/main). The connected components are found by using disjoint set. The used dataset could be downloaded by [link](https://research.yandex.com/blog/benchmarks-for-billion-scale-similarity-search#14h2).

# Prerequisites
> python3.12 is used

1. Install requirements
```bash
pip3 install -r requirements.txt
```

2. Download dataset
```bash
python3 src/download_dataset.py --dataset deep1b
```

# Run

## First configuration
```bash
python3 components.py --M0 64 --M 32 --dataset deep1b
```
## Result
- `level_0`, connected_components = 1;

- `level_1`, connected_components = 1;

- `level_2`, connected_components = 1;

Total connected_components of HNSW = 1.

## Second configuration
```bash
python3 components.py --M0 32 --M 16 --dataset deep1b
```
## Result
- `level_0`, connected_components = 1;

- `level_1`, connected_components = 1;

- `level_2`, connected_components = 1;

Total connected_components of HNSW = 1.

# Conclude
The number of HNSW connected components = 1.
