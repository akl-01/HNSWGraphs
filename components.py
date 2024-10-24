import numpy as np
import argparse
from tqdm import tqdm
# from tqdm import tqdm_notebook as tqdm
from heapq import heappush, heappop
import random
import itertools
random.seed(108)
from src.hnsw import HNSW
from src.hnsw import l2_distance, heuristic
import sys

from concurrent.futures import ThreadPoolExecutor

def brute_force_knn_search(distance_func, k, q, data):
        '''
        Return the list of (idx, dist) for k-closest elements to {x} in {data}
        '''
        return sorted(enumerate(map(lambda x: distance_func(q, x) ,data)), key=lambda a: a[1])[:k]


def calculate_recall(distance_func, kg, test, groundtruth, k, ef, m):
    if groundtruth is None:
        print("Ground truth not found. Calculating ground truth...")
        groundtruth = [ [idx for idx, dist in brute_force_knn_search(distance_func, k, query, kg.data)] for query in tqdm(test)]

    print("Calculating recall...")
    recalls = []
    total_calc = 0
    for query, true_neighbors in tqdm(zip(test, groundtruth), total=len(test)):
        true_neighbors = true_neighbors[:k]  # Use only the top k ground truth neighbors
        entry_points = random.sample(range(len(kg.data)), m)
        observed = [neighbor for neighbor, dist in kg.search(q=query, k=k, ef=ef, return_observed = True)]
        total_calc = total_calc + len(observed)
        results = observed[:k]
        intersection = len(set(true_neighbors).intersection(set(results)))
        # print(f'true_neighbors: {true_neighbors}, results: {results}. Intersection: {intersection}')
        recall = intersection / k
        recalls.append(recall)

    return np.mean(recalls), total_calc/len(test)


def read_fvecs(filename):
    with open(filename, 'rb') as f:
        while True:
            vec_size = np.fromfile(f, dtype=np.int32, count=1)
            if not vec_size:
                break
            vec = np.fromfile(f, dtype=np.float32, count=vec_size[0])
            yield vec


def read_ivecs(filename):
    with open(filename, 'rb') as f:
        while True:
            vec_size = np.fromfile(f, dtype=np.int32, count=1)
            if not vec_size:
                break
            vec = np.fromfile(f, dtype=np.int32, count=vec_size[0])
            yield vec

def read_fbin(filename):
    with open(filename, 'rb') as f:
        n = np.fromfile(f, dtype=np.int32, count=1)[0]
        d = np.fromfile(f, dtype=np.int32, count=1)[0]
        data = np.fromfile(f, dtype=np.float32).reshape(n, d)
        
    return data

def load_deep1b_dataset():
    train_file = "datasets/base.10M.fbin"

    train_data = np.array(list(read_fbin(train_file)))
    return train_data

def load_sift_dataset():
    train_file = 'datasets/siftsmall/siftsmall_base.fvecs'
    test_file = 'datasets/siftsmall/siftsmall_query.fvecs'
    groundtruth_file = 'datasets/siftsmall/siftsmall_groundtruth.ivecs'

    train_data = np.array(list(read_fvecs(train_file)))
    test_data = np.array(list(read_fvecs(test_file)))
    groundtruth_data = np.array(list(read_ivecs(groundtruth_file)))

    return train_data, test_data, groundtruth_data


def generate_synthetic_data(dim, n, nq):
    train_data = np.random.random((n, dim)).astype(np.float32)
    test_data = np.random.random((nq, dim)).astype(np.float32)
    return train_data, test_data


def main():
    parser = argparse.ArgumentParser(description='Test recall of beam search method with KGraph.')
    parser.add_argument('--dataset', choices=['synthetic', 'sift', "deep1b"], default='synthetic', help="Choose the dataset to use: 'synthetic' or 'sift'.")
    parser.add_argument('--K', type=int, default=5, help='The size of the neighbourhood')
    parser.add_argument('--M', type=int, default=50, help='Avg number of neighbors')
    parser.add_argument('--M0', type=int, default=50, help='Avg number of neighbors')
    parser.add_argument('--dim', type=int, default=2, help='Dimensionality of synthetic data (ignored for SIFT).')
    parser.add_argument('--n', type=int, default=200, help='Number of training points for synthetic data (ignored for SIFT).')
    parser.add_argument('--nq', type=int, default=50, help='Number of query points for synthetic data (ignored for SIFT).')
    parser.add_argument('--k', type=int, default=5, help='Number of nearest neighbors to search in the test stage')
    parser.add_argument('--ef', type=int, default=10, help='Size of the beam for beam search.')
    parser.add_argument('--m', type=int, default=3, help='Number of random entry points.')

    args = parser.parse_args()

    # Load dataset
    if args.dataset == 'sift':
        print("Loading SIFT dataset...")
        train_data, test_data, groundtruth_data = load_sift_dataset()
    elif args.dataset == "deep1b":
        print("Loading deep1b dataset...")
        train_data = load_deep1b_dataset()
    else:
        print(f"Generating synthetic dataset with {args.dim}-dimensional space...")
        train_data, test_data = generate_synthetic_data(args.dim, args.n, args.nq)
        groundtruth_data = None

    # Create HNSW
    hnsw = HNSW( distance_func=l2_distance, m=args.M, m0=args.M0, ef=10, ef_construction=64,  neighborhood_construction = heuristic)
    # Add data to HNSW
    def work(i):
        for x in tqdm(train_data[i : i + 1000000]):
            hnsw.add(x)

    with ThreadPoolExecutor(max_workers=10) as executor:
        for i in range(0, 10000000, 1000000):
            executor.submit(work, i)

    print("Start components compute")
    num_components = hnsw.get_components()

    print(f"Components number: {num_components}")

if __name__ == "__main__":
    sys.exit(main() or 0)