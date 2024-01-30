#!/usr/bin/python3

#-----------------------------------------#
#    Multi-Agent PathFinding (MAPF)
#-----------------------------------------#

# --> Group: 07  --> Student: Rita Castro Oliveira

import sys
import subprocess

def readFirstInput(filename):
    input = 0
    line = filename.readline()

    while True and (len(line) != 0):
        if line[0] != "#":
            input = int(line)
            break
        line = filename.readline()
    return input


def readNLines(numberOfLines, filename, list):
    for i in range(numberOfLines):
        line = filename.readline()
        l = line.split()
        list.append([int(l[0]),int(l[1])])

def makeListEdges(numberOfEdges,graphFile,edges):
    for i in range(numberOfEdges):
        line = graphFile.readline()
        l = line.split()
        edges[int(l[0])-1].append(int(l[1]))
        edges[int(l[1])-1].append(int(l[0]))


def main():
    # graph
    numberOfVertices = 0
    numberOfEdges = 0

    #scenario
    numberOfAgents = 0
    initialVertex = list() 
    goalVertex = list() 

    #---> input <---
    graphFileName = sys.argv[1]
    scenarioFileName = sys.argv[2]


    #open, read and close the file graphFile
    graphFile = open(graphFileName)

    numberOfVertices = readFirstInput(graphFile)
    numberOfEdges = int(graphFile.readline())

    edges = list()

    for i in range(numberOfVertices):
        edges.append([i+1])
    makeListEdges(numberOfEdges,graphFile,edges)
    

    graphFile.close()

    #open, read and close the file scenarioFile
    scenarioFile = open(scenarioFileName)

    numberOfAgents = readFirstInput(scenarioFile)

    scenarioFile.readline() # START
    readNLines(numberOfAgents,scenarioFile,initialVertex)

    scenarioFile.readline() # GOAL
    readNLines(numberOfAgents,scenarioFile,goalVertex)

    scenarioFile.close()


    #---> minizinc <---

    dataFile = open("dataMAPF.dzn", "w")
    data = "nvertices=" + str(numberOfVertices) + ';\n'
    data += "nedges=" + str(numberOfEdges) + ';\n'

    data += "edges=["
    for i in range(numberOfVertices):
        if i!=0: data += ","
        n = len(edges[i])
        data += "{"
        for j in range(n):
            data += str(edges[i][j])
            if j!=n-1: data+= ","
        data += "}"
    data+= "];\n"

    data += "nagents=" + str(numberOfAgents) + ';\n'
    data+= "start=[" + str(initialVertex[0][1])
    for i in range(1,numberOfAgents):
        data+= "," + str(initialVertex[i][1])
    data+= "];\n"
    data+= "goal=[" + str(goalVertex[0][1])
    for i in range(1,numberOfAgents):
        data+= "," + str(goalVertex[i][1])
    data+= "];\n"
    
    numberOfMakespan = 1 + int(numberOfAgents/4)
    while True:
        time = "maxtimestep = " + str(numberOfMakespan) + ";"
        dataFile = open("dataMAPF.dzn", "w")
        dataFile.write(data + time)
        dataFile.close()

        output = subprocess.run(["minizinc --solver gecode makespanMAPF.mzn dataMAPF.dzn"], shell=True,stdout=subprocess.PIPE,universal_newlines=True)
        result = output.stdout.split('\n')
        
        if "=====UNSATISFIABLE=====" not in result:
            break

        numberOfMakespan += 1 + int(numberOfAgents/10)

    #---> output <---
    if "==========" in result: result.remove("==========")
    if "----------" in result: result.remove("----------")
    if "" in result: result.remove("")

    print(*result, sep = "\n")
        

if __name__ == '__main__':
    main()
