mkdir ./tests/$1
wget $2 ./tests/$1/airfoil.dat
# -d --surface
# -o --output_mesh
# -f --farfield_grid
# -s --surface
python3 create_mesh.py -s ./tests/$1/airfoil.dat -o ./tests/$1/$1.su2 -f 1e-4 -s 1e-2
echo "MESH_FILENAME= $1.su2" > ./tests/$1/$1.cfg;
