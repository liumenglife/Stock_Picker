import sys
import csv
import os
import numpy as np

# Returns mean of an input list, or 0 if the length of the list is 0
def mean( inpList ):
    return np.mean( inpList )

# Returns variance given an input list
def variance( inpList ):
    return np.var( inpList )

# Loads csv and returns as a 2d list array
def loadSheet( filename ):
    rawList = []
    with open( filename, 'r' ) as csvfile:
        csvReader = csv.reader( csvfile, delimiter=',', quotechar='"' )
        for row in csvReader:
            rawList.append( row )
    return rawList

# Writes a 2d list array to a csv
def writeSheet( filename, inpList ):
    with open( filename, 'w' ) as csvfile:
        csvWriter = csv.writer( csvfile, delimiter=',', quotechar='"' )
        for row in inpList:
            csvWriter.writerow( row )

# Auto tester
def auto_test( ):
    print( "Runing Picker eztools tests" )
    passed = 0;
    try:
        ########################################################################
        ## Add new tests in below here
        ########################################################################
        result = mean( [1, 2, 3] )
        if result != 2: raise ValueError(passed, result)
        passed += 1

        result = mean([])
        if result != 0: raise ValueError(passed, result)
        passed += 1

        result = variance([1, 2, 3, 4, 5])
        if result != 2.5: raise ValueError(passed, result)
        passed += 1

        result = variance([])
        if result != 0: raise ValueError(passed, result)
        passed += 1


        ########################################################################
        print("Congratulations! All tests passed successfully")
    except ValueError as err:
        print("### Test " + str(err.args[0]) + " failed with result of " + str(err.args[1]) + " ###")

if __name__ == "__main__":
    auto_test()
