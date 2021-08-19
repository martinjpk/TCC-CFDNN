import argparse
from src.mesh import Mesh

def main(filename, output):
    t = Mesh('airfoil', filename, 1e-2, 1e-4, 3)
    t.genPoints()
    t.write(output)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--filename', type=str)
    parser.add_argument('-o', '--output_mesh', type=str)
    parser.add_argument('-f', '--farfield-grid', type=float)
    parser.add_argument('-s', '--surface-grid', type=float)

if __name__ == '__main__':
    args = parse_args()
    main(args)
