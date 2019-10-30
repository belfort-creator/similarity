import argparse
import os
import networkx as nx
from networkx.drawing.nx_pydot import write_dot
import itertools

def jaccard(set1, set2):

    intersection = set1.intersection(set2)
    intersection_length = float(len(intersection))
    union = set1.union(set2)
    union_length = float(len(union))
    return intersection_length / union_length

def get_strings(fullpath):

    strings = os.popen("strings '{0}'".format(fullpath)).read()
    strings = set(strings.split("\n"))
    return strings

def pecheck(fullpath):

    return open(fullpath).read(2) == "MZ"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Identify similarities between malware samples and build similarity groups"
    )

    parser.add_argument(
        "target_dictionary",
        help="Directory containing malware"
    )

    parser.add_argument(
        "output_dot_file",
        help="Where to save the output graph DOT file"
    )

    parser.add_argument(
        "--jaccard_index_threshold", "-j", dest="threshold", type=float,
        default=0.8, help="Threshold above which to create an 'edge' betweem samples"
    )

    args = parser.parse_args()

    malware_paths = []
    malware_features = dict()
    graph = nx.Graph()

    for root, dirs, paths in os.walk(args.target_dictionary):
        for path in paths:
            full_path = os.path.join(root, path)
            malware_paths.append(full_path)

    malware_paths = filter(pecheck, malware_paths)

    for path in malware_paths:

        features = get_strings(path)
        print("Extracted {0} features from {1} ...".format(len(features), path))
        malware_features[path] = features

        graph.add_node(path, label=os.path.split(path)[-1][:10])

    for malware1, malware2 in itertools.combinations(malware_paths, 2):
        jaccard_index = jaccard(malware_features[malware1], malware_features[malware2])
        if jaccard_index > args.threshold:
            print malware1, malware2, jaccard_index
            graph.add_edge(malware1, malware2, penwidth=1+(jaccard_index-args.threshold)*10)

    write_dot(graph, args.output_dot_file)