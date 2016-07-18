import csv
import sys
from sets import *

if __name__ == "__main__":
    if len(sys.argv) < 2:
	print "Uso: <arquivo csv com tarefas do Como e Campina>"
	sys.exit(1)

    images = Set([])
	
    with open(sys.argv[1], 'rb') as csvfile:
	csvreader = csv.reader(csvfile)
	for row in csvreader:
		photosInfo = row[3].strip("{}").split(",")

		photo1 = "https:" + photosInfo[1].split(":")[2].strip(" \"{}")
		photo2 = "https:" + photosInfo[2].split(":")[2].strip(" \"{}")
		photo3 = "https:" + photosInfo[3].split(":")[2].strip(" \"{}")
		photo4 = "https:" + photosInfo[4].split(":")[2].strip(" \"{}")

		images.add(photo1)
		images.add(photo2)
		images.add(photo3)
		images.add(photo4)


    #Building new tasks!
    print "question,url_a"
    for image in images:
	print "agradavel,"+image
	print "seguro,"+image
