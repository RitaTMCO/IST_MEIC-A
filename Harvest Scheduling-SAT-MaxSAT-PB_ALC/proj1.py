#!/usr/bin/python3

#-----------------------------------------#
#    Harvest Scheduling Problem
#-----------------------------------------#

# --> Group: 02  --> Student: Rita Castro Oliveira

from pysat.solvers import *
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from pysat.pb import *
from pysat.card import CardEnc, EncType

import itertools

def readNLines(numberOfLines,res):
    for i in range(numberOfLines):
        res.append(list())
        line = input()
        data = line.split()
        lenData = len(data)
        for j in range(lenData):
            res[i].append(int(data[j]))
    return res

def adjacentList(numberOfLines,res1,res2,res3):
    for u in range(numberOfLines):
        res2.append(list())
        line = input()
        data = line.split()
        n=int(data[0])
        res3.append(n)
        for a in range(n):
            if [u+1,int(data[a+1])] not in res1 and [int(data[a+1]),u+1] not in res1:
                res1.append([u+1,int(data[a+1])])
            res2[u].append(int(data[a+1]))
    return res1.sort(),res2,res3

def readInput():
    numberOfUnits = int(input())

    numberOfPeriods = int(input())

    areaSizeOfUnit = list() # size of each unit
    line = input().split()
    for i in range(numberOfUnits):
        areaSizeOfUnit.append(int(line[i]))

    adjacentUnits = list() # all adjacents that exists in the problem
    adjacentofEachUnit = list() #adjacents of each unit
    numberOfAdjacents = list() # number of adjacents of each unit
    adjacentList(numberOfUnits,adjacentUnits,adjacentofEachUnit,numberOfAdjacents)

    profitOfUnits = list()
    readNLines(numberOfPeriods,profitOfUnits)

    miniAreaSize = int(input())

    return numberOfUnits, numberOfPeriods,areaSizeOfUnit,adjacentUnits,adjacentofEachUnit,numberOfAdjacents,profitOfUnits,miniAreaSize


def createVariables(numberOfUnits,numberOfPeriods,numberOfAdjacents):
    u = [[i+1 + j*numberOfUnits for j in range(numberOfPeriods)] for i in range(numberOfUnits)]

    p = list()
    for i in  range(numberOfUnits):
        add = numberOfPeriods*numberOfUnits 
        if i != 0:
            add = p[i-1][-1]
        p += [[add + 1 + j  for j in range(numberOfAdjacents[i] + 1)]]
    
    d = list()
    for i in  range(numberOfUnits):
        add = p[-1][-1]
        if i != 0:
            add = d[i-1][-1]
        d += [[add + 1 + j  for j in range(numberOfUnits)]]
    
    natural = [ d[-1][-1] + 1 + i for i in range(numberOfUnits)]
    
    return u,natural,p,d


def showOutput(num, lis):
    output = str(num)
    for i in range(num):
        output+= " " + str(lis[i])
    print(output)


def writeOutput(profit,unitsHarvested,unitsOfNaturalReserve,numberOfPeriods,model):
    print(profit)
    for i in range(numberOfPeriods):
        if model != None:
            showOutput(len(unitsHarvested[i]),unitsHarvested[i])
        else:
            print(0)
    if model != None:
        showOutput(len(unitsOfNaturalReserve),unitsOfNaturalReserve)
    else:
        print(0)


def main():

    #---> Input <---
    numberOfUnits, numberOfPeriods,areaSizeOfUnit,adjacentUnits,adjacentofEachUnit,numberOfAdjacents,profitOfUnits,miniAreaSize = readInput()


    #--->  Variables <---
    # variable uij => unit i in period j
    # variable naturali =>  identifies if unit i is in natural reserve
    # variable pij => denotes if unit j (neighbours of unit i) is  predecessor of unit i. It will be used in Tree-based contiguity formulation
    # variable dil => denotes if unit i is at depth l in the tree
    u,natural,p,d = createVariables(numberOfUnits,numberOfPeriods,numberOfAdjacents)


    #---> Constraints <---
    # Constraint 1: Two adjacent units (i.e. units that share a common frontier) cannot be harvested in the same time period -> -uip \/ -ujp (i and j are adjacent units in period p)
    # Constraint 2: Each unit of land cannot be harvested more than once in the T time periods -> - uip1 \/ -uip2 (unit i in period p1 and in period p2)
    # Constraint 3: If unit i is harvested once in the T time periods then unit i cannot be in natural reserve ->  -(ui1 \/ -naturali) /\ .../\ -(uiT \/ -naturali) 
    # Constraint 4: Goal is to help building the harvest schedule of the agricultural area such that the profit is maximized. (Maximum Satisfiability)
    # Constraint 5: The natural reserve must be a contiguous area with a given minimum area size of Amin such that Amin is bigger or equals than 0 (Pseudo-Boolean Satisfiability)

    #------Tree-based contiguity formulation-------
    # Constraint 6: If unit i is root of tree then unit i is in natural reserve -> - pi0 \/ naturali
    # Constraint 7: If unit i is in natural reserve then exists a tree with root -> naturali -> p10 \/..\/ pU0
    # Constraint 8: If unit i is in natural reserve then unit i is in tree (it is root or some unit j is its prodecessor of unit i (pij) or it is predecessor of some unit j (pji))
    # -> ( -natural i \/ pi0 \/... \/ pij \/... \/ pji) 
    # Constraint 9: If unit i is not in natural reserve then it is not in tree -> (natural i \/ -pi0) /\ ... /\ (natural i \/ -pij) /\ ... /\ (natural i \/ -pji)
    # Constraint 10: If it exists relation pji then unit i and unit j are in tree at some depth: pij-> di1 \/ ... \/ diM \/ dj1 \/ ... \/ djM
    # Constraint 11: If unit i is in natural reserve and is in tree at depth l then must have one neighbor as predecessor in the tree or 0 if unit i is the root.
    # pi0 + ... + pij <=1 and di1 \/...\/ d1M -> pi1 \/ ... \/ pij
    # Constraint 12: A root node is always at depth 1 -> (-pi0 \/ di1) /\ (pi0 \/ -di1)
    # Constraint 13: Each unit can only be assigned a single depth -> di1 + ... + diU <= 1
    # Constraint 14: If two adjacent units i,j are in natural reserve then they have a relation in tree. Or unit i is predesessor of unit j or unit j is predesessor of unit i in tree
    # naturalj /\ naturali -> -pji \/ -pij
    # Constraint 15: If unit i is predesessor of unit j then units i,j are in natural reserve -> (naturalj \/ - pji) /\ (naturali \/ - pji)
    # Constraint 16: The depth of unit i is one more than its predecessor -> (djl /\ dil+1 -> pij) /\ (djl /\  pij -> dil+1) /\ (dil+1 /\ pij -> djl)
    # Constraint 17: The nodes at depth numberOfUnits must be leaves of the tree, i.e., these nodes cannot be predecessors of other node: -pij \/ -djM
    # Constraint 18: It must exist one tree with one root: p10 + p20 + ..+ p1U <=1

    solver = RC2(WCNF())

    # Constrait 1
    for per in range(numberOfPeriods):
        for unit1, unit2 in adjacentUnits:
            solver.add_clause([-u[unit1-1][per], -u[unit2-1][per]])



    p0 = [p[i][0] for i in range(numberOfUnits)]
    for unitI in range(numberOfUnits):

        #Constrait 2
        for period1,period2 in itertools.product(range(numberOfPeriods),range(numberOfPeriods)):
            if period1 != period2:
                solver.add_clause([-u[unitI][period1], -u[unitI][period2]])


        #Constrait 6
        solver.add_clause([-p0[unitI],natural[unitI]])

        #Constrait 7
        solver.add_clause([-natural[unitI]]+p0)

        # Constraint 8
        inReserve = [-natural[unitI]] + p[unitI]
        # Constraint 9
        solver.add_clause([natural[unitI],-p[unitI][0]])

        for j in range(1,numberOfAdjacents[unitI]+1):
            unitJ = adjacentofEachUnit[unitI][j-1] -1 # adjacent of unit ui (uj)
            i = adjacentofEachUnit[unitJ].index(unitI+1) + 1 # index of u2 in p[u1] (p[u1][0] is relation between root and unit i)

            # Constraint 8
            inReserve.append(p[unitJ][i])

            # Constraint 9
            solver.add_clause([natural[unitI],-p[unitI][j]])
            solver.add_clause([natural[unitI],-p[unitJ][i]])

            # Constraint 10
            solver.add_clause([-p[unitJ][i]] + d[unitI] + d[unitJ])
        # Constraint 8
        solver.add_clause(inReserve)

        # Constraint 11
        for l in range(numberOfUnits):
            solver.add_clause([-d[unitI][l]] + p[unitI])

        enc1 = CardEnc.atmost(lits=p[unitI], bound=1, top_id=(numberOfAdjacents[unitI] + 1), encoding=EncType.pairwise)
        for clause in enc1.clauses:
            solver.add_clause(clause) 

        # Constraint 12
        solver.add_clause([-p[unitI][0],d[unitI][0]])
        solver.add_clause([-d[unitI][0],p[unitI][0]])

        # Constraint 13
        enc2 = CardEnc.atmost(lits=d[unit1], bound=1, top_id=numberOfUnits, encoding=EncType.pairwise)
        for clause in enc2.clauses:
            solver.add_clause(clause)
        


    for x,per in itertools.product(range(numberOfUnits),range(numberOfPeriods)):
        # Constraint 3
        solver.add_clause([-u[x][per],-natural[x]]) 
        # Constraint 4
        solver.add_clause([u[x][per]], weight=profitOfUnits[per][x])
    
    

    for uj, ui in adjacentUnits:
        i = adjacentofEachUnit[uj-1].index(ui) + 1 # index of u2 in p[u1]
        j = adjacentofEachUnit[ui-1].index(uj) + 1 #index of u1 in p[u2]

        # Constraint 14
        solver.add_clause([-natural[uj-1],-natural[ui-1], -p[uj-1][i],-p[ui-1][j]])

        # Constraint 15
        solver.add_clause([natural[uj-1],-p[uj-1][i]])
        solver.add_clause([natural[ui-1],-p[uj-1][i]])
        solver.add_clause([natural[uj-1],-p[ui-1][j]])
        solver.add_clause([natural[ui-1],-p[ui-1][j]])

    
    for u1 in range(numberOfUnits):
        for i in range(numberOfAdjacents[u1]):
            
            u2 = adjacentofEachUnit[u1][i] - 1 # id of adjacent - 1
            j = adjacentofEachUnit[u2].index(u1+1) + 1 #index of u1+1 in p[u2]

            # Constraint 16
            for r in range(numberOfUnits-1):
                solver.add_clause([-d[u1][r],-d[u2][r+1],p[u2][j]])
                solver.add_clause([-d[u1][r],d[u2][r+1],-p[u2][j]])
                solver.add_clause([d[u1][r],-d[u2][r+1],-p[u2][j]])
            
            # Constraint 17
            solver.add_clause([-p[u1][i],-d[u2][-1]])
    
    # Constraint 18
    enc3 = CardEnc.atmost(lits=p0, bound=1, top_id=numberOfUnits, encoding=EncType.pairwise)
    for clause in enc3.clauses:
        solver.add_clause(clause)   

    # Constraint 5
    cnf = PBEnc.atleast(lits=natural, weights=areaSizeOfUnit, bound=miniAreaSize)
    clauses = cnf.clauses
    for c in clauses:
        solver.add_clause(c)
    


    #---> Model <---
    model = solver.compute()

    if model!=None:
        l1 = d[-1][-1]
        l2 = d[-1][-1] + numberOfUnits
        model = model[:(numberOfPeriods*numberOfUnits)] + model[l1:l2]

    profit = 0
    unitsHarvested = list()
    for i in range(numberOfPeriods):
        unitsHarvested.append(list())
    unitsOfNaturalReserve = list()

    if model!=None:
        for i in range((numberOfPeriods*numberOfUnits)+numberOfUnits):
            if model[i] > 0 and i<numberOfPeriods*numberOfUnits:
                period = int(i/numberOfUnits)
                idUnit = i%numberOfUnits
                profit+=profitOfUnits[period][idUnit]
                unitsHarvested[period].append(idUnit+1)
            elif model[i] > 0 and i>=numberOfPeriods*numberOfUnits:
                idUnit = i%numberOfUnits
                unitsOfNaturalReserve.append(idUnit+1)
       

    #---> Output <---
    writeOutput(profit,unitsHarvested,unitsOfNaturalReserve,numberOfPeriods,model)



if __name__ == '__main__':
    main()