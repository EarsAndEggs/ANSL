import fnmatch
import os
from num2words import num2words

def fileIterate(audioDir: str):   
    print(audioDir)
    outputDir = audioDir+"/processed"
    print(outputDir)

    files = os.listdir(audioDir)
    for file in files:
        fileName = os.fsdecode(file)
        if fileName.endswith(".mp3"): 

            wavImportNumber = len([True for file in files if file.endswith(".mp3")])
            print(f"{wavImportNumber} audio clips remaining for processing")
            
            filePath = os.path.join(audioDir, fileName)
            fileSize = os.path.getsize(filePath)
            print(f"Playing: {filePath} with: {fileSize} bytes of data")

            play_audio = True
            while play_audio:
                #playsound(fileName)
                
                inputTranscription = input("Enter transcription: ")
                choice = input("Repeat audio clip? (y/n) ")

                while choice.lower() not in ('y', 'n'):
                    choice = input("Invalid input, please type either (y/n)")
                
                if choice == 'y':
                    print("Repeating audio clip")
                elif choice == 'n':
                    play_audio = False
                    cleanedTranscription = tNum2Word(inputTranscription)
                    print(cleanedTranscription)

                    csvAppend(filePath,fileSize,cleanedTranscription)

                    print("Moving on to next audio clip")
                    break

    print("Finished transcription")


def tNum2Word(transcription: str) -> str:
    """Converts a list of numbers to there written format. If the transcription contains words handle this correctly.

    Args:
        n (str): string of single digit numbers. May contain non integers as well.

    Returns:pyth
        str: transcrition with numbers as text
    """
    NUMS = ["0","1","2","3","4","5","6","7","8","9"]
    
    word = ""
    transcriptionList = []
    for char in transcription:
        if char in NUMS:
            # If previous char was non number append to list
            if word != "":
                transcriptionList.append(word.strip())
                word = ""
            transcriptionList.append(num2words(int(char)))
        # Combine text into a single element of list
        else:
            word += char

    # If transciption ends with non number
    if word != "": 
        transcriptionList.append(word)
    
    return " ".join(transcriptionList)

        
def csvAppend(path,bytes,transcription):
    return

def csvSplit():
    inputcsvDir = os.getcwd()+"\output\output.csv"

def csvScramble():
    return

fileIterate("/Users/jack/Downloads")