#!/usr/bin/python3

#-----------------------------------------#
#    Harvest Scheduling Problem
#-----------------------------------------#

# --> Group: 02  --> Student: Rita Castro Oliveira

from z3 import Optimize,Int,Bool,If,Implies,Sum,Or,sat

def readNLines(numberOfLines,res):
    for i in range(numberOfLines):
        res.append(list())
        line = input()
        data = line.split()
        lenData = len(data)
        for j in range(lenData):
            res[i].append(int(data[j]))
    return res

def adjacentList(numberOfLines,res1,res2):
    for u in range(numberOfLines):
        res2.append(list())
        line = input()
        data = line.split()
        n=int(data[0])
        for a in range(n):
            if [u+1,int(data[a+1])] not in res1 and [int(data[a+1]),u+1] not in res1:
                res1.append([u+1,int(data[a+1])])
            res2[u].append(int(data[a+1]))
    return res1.sort(),res2

def readInput():
    numberOfUnits = int(input())

    numberOfPeriods = int(input())

    areaSizeOfUnit = list() # size of each unit
    line = input().split()
    for i in range(numberOfUnits):
        areaSizeOfUnit.append(int(line[i]))

    adjacentUnits = list() # all adjacents that exist in the problem
    adjacentofEachUnit = list() #adjacents of each unit
    adjacentList(numberOfUnits,adjacentUnits,adjacentofEachUnit)

    profitOfUnits = list()
    readNLines(numberOfPeriods,profitOfUnits)

    miniAreaSize = int(input())

    return numberOfUnits, numberOfPeriods,areaSizeOfUnit,adjacentUnits,adjacentofEachUnit,profitOfUnits,miniAreaSize


def createVariablesAndFunctions(numberOfPeriods,numberOfUnits):
    #variable ni =>  identifies if unit i is in natural reserve. O if unit i is not in natural reserve and 1 if it is in natural reserve
    #variable dij => denotes if unit i is at depth j in the tree. True if unit i is in the tree and False if it is not in the tree 
    #variable pij => unit i in period j. O if unit i was not harvested in period j and 1 if unit i was harvested in period j
    n = [ Int(f'n_{i+1}') for i in range(numberOfUnits)]
    d = [ [Bool(f'd_{i+1}_{j+1}') for j in range(numberOfUnits)] for i in range(numberOfUnits)]
    p = [ [Int(f'p_{i+1}_{j+1}') for j in range(numberOfPeriods)] for i in range(numberOfUnits)]
    return n,d,p


def analyzeModel(model,profitOfUnits,numberOfUnits,numberOfPeriods,n,p,check):
    profit=0
    unitsHarvested = list()
    unitsOfNaturalReserve = list()
    for i in range(numberOfPeriods):
        unitsHarvested.append(list())

    if check == sat:
        for i in range(numberOfUnits):
            for j in range(numberOfPeriods):
                if model[p[i][j]].as_long():
                    profit += profitOfUnits[j][i]
                    unitsHarvested[j].append(i+1)
            if model[n[i]].as_long():
                unitsOfNaturalReserve.append(i+1)

    return profit,unitsHarvested,unitsOfNaturalReserve


def showOutput(num,lis):
    output = str(num)
    for i in range(num):
        output+= " " + str(lis[i])
    print(output)


def writeOutput(profit,unitsHarvested,unitsOfNaturalReserve,numberOfPeriods):
    print(profit)
    for i in range(numberOfPeriods):
        showOutput(len(unitsHarvested[i]),unitsHarvested[i])
    showOutput(len(unitsOfNaturalReserve),unitsOfNaturalReserve)


def createConstraints(n,d,p,numberOfUnits, numberOfPeriods,areaSizeOfUnit,adjacentUnits,adjacentofEachUnit,profitOfUnits,miniAreaSize):
    s = Optimize()

    min = list()
    max = list()
    root = list()

    for i in range(numberOfUnits):
        #Each unit of land cannot be harvested more than once in the T time periods
        for j in range(numberOfPeriods):
            # Variable pij has value 0 or value 1
            s.add(Or(p[i][j]==0,p[i][j]==1))
            max.append(p[i][j]*profitOfUnits[j][i])
        sumP = Sum(p[i])
        s.add(sumP <= 1)
    
        # Variable ni has value 0 or value 1
        s.add(Or(n[i]==0,n[i]==1))

        #If unit i is harvested once in the T time periods then unit i cannot be in natural reserve
        s.add(Implies(sumP!=0,n[i]!=1))

        min.append(areaSizeOfUnit[i]*n[i])

        #If unit i is root of tree then unit i is in natural reserve
        s.add(Implies(d[i][0],n[i]==1))

        #If unit i is at depth j in the tree then one or more neighbors of unit i is at depth j-1, this is, they are predecessors of unit i
        for j in range(numberOfUnits): 
            if j!=0:
                neighbors = [d[a-1][j-1] for a in adjacentofEachUnit[i]]
                s.add(Implies(d[i][j],Or(neighbors)))

        #To unit i can only be assigned a single depth. If unit i is in natural reserve then unit i is in tree. If unit i is not in natural reserve then unit i is not in tree
        listD = [If(d[i][j],1,0) for j in range(numberOfUnits)] 
        sumD = Sum(listD)
        s.add(If(n[i]==1,sumD==1,sumD==0))
        
        root.append(If(d[i][0],1,0))
        

    #The natural reserve must be a contiguous area with a given minimum area size of Amin such that Amin >= 0.
    sumMin = Sum(min)
    s.add(sumMin >= miniAreaSize)

    # If one or more units is in the tree then it exists a tree with one root
    sumRoot = Sum(root)
    sumN = Sum(n)
    s.add(Implies(sumN>=1,sumRoot==1))

   
    #Two adjacent units (i.e. units that share a common frontier) cannot be harvested in the same time period
    for i,a in adjacentUnits:
        for j in range(numberOfPeriods):
            s.add(p[i-1][j]+p[a-1][j]<=1)
    
    #Goal is to help building the harvest schedule of the agricultural area such that the profit is maximized
    sumMax = Sum(max)
    s.maximize(sumMax)

    return s


def main():

    #---> Input <---
    numberOfUnits, numberOfPeriods,areaSizeOfUnit,adjacentUnits,adjacentofEachUnit,profitOfUnits,miniAreaSize = readInput()


    #---> Variables <---
    n,d,p = createVariablesAndFunctions(numberOfPeriods,numberOfUnits)


    #---> Constraints <---
    solver = createConstraints(n,d,p,numberOfUnits,numberOfPeriods,areaSizeOfUnit,adjacentUnits,adjacentofEachUnit,profitOfUnits,miniAreaSize)

    check = solver.check()
    model = solver.model()
    
    # ---> Model <---
    profit,unitsHarvested,unitsOfNaturalReserve = analyzeModel(model,profitOfUnits,numberOfUnits,numberOfPeriods,n,p,check)


    #---> Output <---
    writeOutput(profit,unitsHarvested,unitsOfNaturalReserve,numberOfPeriods)


if __name__ == '__main__':
    main()
