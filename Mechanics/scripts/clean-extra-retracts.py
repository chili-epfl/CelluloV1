#!/usr/bin/python3
import argparse
import os
import sys

if __name__ == '__main__':

    #Input output file names
    parser = argparse.ArgumentParser(description='Cleans unnecessary retract movements from a gcode file.')
    parser.add_argument("INPUT", help="input gcode file")
    parser.add_argument("-o", "--output", help="output gcode file")
    args = parser.parse_args()

    if os.path.isfile(args.INPUT):
        print("Input file: " + args.INPUT)
        if not args.output:
            newoutput = args.INPUT
            if newoutput.lower().endswith(".gcode"):
                newoutput = newoutput[:-6]
            newoutput += "-cleaned.gcode"
            args.output = newoutput
        print("Output file: " + args.output)
    else:
        print("Input file " + args.INPUT + " not found.")
        sys.exit(1)

    with open(args.INPUT,'r') as inputfile, open(args.output,'w') as outputfile:
        prevline = inputfile.readline()
        prevlineWasRetract = False
        numretractscleaned = 0
        numretractsleft = 0
        prevExtrude = 0.0
        prevPrevExtrude = 0.0
        while True:
            currentline = inputfile.readline()

            #End of file
            if currentline == "":
                outputfile.write(prevline)
                break

            #Actual line parsing
            if (currentline.startswith("G1") and
                "E" in currentline and
                "F" in currentline and
                (not "X" in currentline) and
                (not "Y" in currentline) and
                (not "Z" in currentline)):

                #Get current extrude
                tokens = currentline.split(" ")
                currentExtrude = 0.0
                for token in tokens:
                    if token.startswith("E"):
                        currentExtrude = float(token[1:])
                        break

                #Compare prev lines
                if prevlineWasRetract and currentExtrude == prevPrevExtrude:
                    numretractscleaned += 2
                    print("Cleaned lines:\n" + prevline + currentline + "\n")
                    prevline = inputfile.readline()
                    prevlineWasRetract = False

                    prevExtrude = prevPrevExtrude
                    currentExtrude = prevPrevExtrude
                else:
                    outputfile.write(prevline)
                    prevline = currentline
                    prevlineWasRetract = True

                prevPrevExtrude = prevExtrude
                prevExtrude = currentExtrude
            else:
                if prevlineWasRetract:
                    numretractsleft += 1
                outputfile.write(prevline)
                prevline = currentline
                prevlineWasRetract = False

        print("Number of retracts cleaned: " + str(numretractscleaned))
        print("Number of retracts left alone: " + str(numretractsleft))
