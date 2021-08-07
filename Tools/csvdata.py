from playsound import playsound
import fnmatch
import csv
import os
import math
import glob
from num2words import num2words

def fileIterate():
    inputDir = os.getcwd()      
    print(inputDir)
    outputDir = os.getcwd()+"\output"
    print(outputDir)

    for file in os.listdir(inputDir):
        fileName = os.fsdecode(file)
        if fileName.endswith(".mp3"): 
            wavImportNumber = len(fnmatch.filter(os.listdir(inputDir), '*.mp3'))
            print(str(wavImportNumber) + " audio clips remaining for processing")
            
            filePath = os.path.join(inputDir, fileName)
            fileSize = os.path.getsize(filePath)
            print("Playing: " + filePath + " with: " + str(fileSize) + " bytes of data")

            while True:
                #playsound(fileName)
                
                inputTranscription = input("Enter transcription: ")
                choice = input("Repeat audio clip? (y/n) ")

                while choice not in ('y', 'n'):
                    print("Invalid input, please type either (y/n)")
                if choice == 'y':
                    print("Repeating audio clip")
                    continue
                if choice == 'n':
                    inputTranscription = int(inputTranscription)
                    cleanedTranscription = tNum2Word(inputTranscription)
                    print(cleanedTranscription)

                    csvAppend(filePath,fileSize,cleanedTranscription)

                    print("Moving on to next audio clip")
                    break
            continue
        else:
            continue

    print("Finished transcription")

def tNum2Word(n):
    digits = [num2words((n//(10**i))%10) for i in range(math.ceil(math.log(n, 10)), -1, -1)][bool(math.log(n,10)%1):]
    return digits

def csvAppend(path,bytes,transcription):
    return

def csvSplit():
    inputcsvDir = os.getcwd()+"\output\output.csv"

def csvScramble():
    return

fileIterate()