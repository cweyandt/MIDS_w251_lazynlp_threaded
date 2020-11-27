#import lazynlp
import analytics
from create import filter_files
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("path", help="path containing links")
parser.add_argument("--recursive", help="indicates that path contains folders instead of files", action="store_true")
parser.add_argument("--delete", help="delete duplicate files", action="store_true")
args = parser.parse_args()

if args.recursive:
	path = os.path.abspath(args.path)
	paths = [ os.path.join(path,name) for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]
	print( "paths found: " + str(len(paths)) )
else:
	paths = [os.path.abspath(args.path)]

files = []

for dir in paths:
	file_list = os.listdir(dir)
	print (f'Files in {dir}: {len(file_list)}')
	if len(file_list) == 0:
		continue
	for file in file_list:
		files.append(os.path.join(dir,file))

print ( 'files found: ' + str(len(files)) )	

filter_files(files, threshold=0.5, gran='word', n=8, capacity=100000000, error_rate=1e-7, header=0, interval=1000000)

if args.delete:
	dups = open('dupped_files.txt','r')
	count = 0
	for file in dups:
		os.remove(file)
		count += 1
	print (f'Removed {dups} duplicate files.')
