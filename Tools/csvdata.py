import os
import sys
import csv
import math
import random
import json

from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename

from num2words import num2words
from pydub import AudioSegment
from pydub.playback import play

def file_iterate(audio_dir: str):
    """ file_iterate goes over each mp3 file and provides the ability to transcribe them


    Args:
        audio_dir (str): directory that contains the audio clips to be transcribed
    """
    input("IMPORTANT: A Manifest file for transcription data MUST be selected or created before continuing! Before continuing, please create a manifest file for output while the program is paused. To continue, input any key")
    
    tk = Tk()
    tk.overrideredirect(True)
    tk.lift()
    tk.attributes('-topmost',True)
    tk.after_idle(tk.attributes,'-topmost',False)
    
    processed_dir = audio_dir+"/processed"
    if not os.path.exists(processed_dir):
        os.makedirs(audio_dir+processed_dir)
        
    deleted_dir = audio_dir+"/deleted"
    if not os.path.exists(deleted_dir):
        os.makedirs(audio_dir+deleted_dir)
        
    manifest_path = askopenfilename(initialdir=f'"{audio_dir}"',types=[("JSON file","*.json")], title='Select Manifest file')
    tk.withdraw

    if manifest_path == "":
        sys.exit("Manifest File was NOT selected, please make sure to create a manifest file for transcription before using this function. Stopping execution!")
    else:            

        audio_files = os.listdir(audio_dir)
        for audio_file in audio_files:
            file_name = os.fsdecode(audio_file)
            if file_name.endswith(".wav"):

                wav_import_number = len([True for audio_file in audio_files if audio_file.endswith(".wav")])
                print(f"{wav_import_number} audio clips remaining for processing")

                file_path = os.path.join(audio_dir, file_name)
                processed_path = os.path.join(processed_dir, file_name)
                deleted_path = os.path.join(deleted_dir, file_name)
                
                audiofile = AudioSegment.from_file(file_path)
                audio_duration = audiofile.duration_seconds
                
                print(f"Playing: {file_path} with: {audio} seconds of data")

                play_audio = True
                while play_audio:
                    ans = input("Should this audio file be deleted? (y/n) ")
                    
                    while ans not in ('y', 'n','Y','N'):
                        ans = input("Invalid input, please type either (y/n)")
                        
                    if ans == "Y" or choice == "y":
                        os.rename(file_path,deleted_path)
                        print("Deleted " + file_path + ", moving on to next audio clip")
                    elif ans == "N" or choice == "n":
                        # play transcription to check accuracy
                        audio = AudioSegment.from_mp3(file_path)
                        play(audio)

                        input_transcription = input("Enter transcription: ")
                        choice = input("Repeat audio clip? (y/n) ")

                        while choice not in ('y', 'n','Y','N'):
                            choice = input("Invalid input, please type either (y/n)")

                        if choice == 'y' or choice == 'Y':
                            print("Repeating audio clip")
                            
                        elif choice == 'n' or choice == 'N':
                            play_audio = False
                            expanded_transcription = replacements(input_transcription)
                            cleaned_transcription = transcibe_num2word(expanded_transcription)
                            print(cleaned_transcription)

                            json_append(manifest_path,file_path,cleaned_transcription,audio_duration)
                            
                            os.rename(file_path,processed_path)

                            print("Appended to manifest file, moving on to next audio clip")
                            break

    print("All files have now been processed! Please check the manifest file for any inconsistencies!")


def transcibe_num2word(transcription: str) -> str:
    """transcribe_num2word converts a list of ints to a written format. If contains words handle this correctly.

    Args:
        n (str): string of single digit numbers. May contain non integers as well.

    Returns:pyth
        str: transcrition with numbers as text
    """
    NUMS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    word = ""
    transcription_list = []
    for char in transcription:
        if char in NUMS:
            # If previous char was non number append to list
            if word != "":
                transcription_list.append(word.strip())
                word = ""
            transcription_list.append(num2words(int(char)))
        # Combine text into a single element of list
        else:
            word += char

    # If transciption ends with non number
    if word != "":
        transcription_list.append(word)

    return " ".join(transcription_list)


def json_append(manifest_file: str, filepath: str, transcription: str, duration: int) -> None:
    """ json_append writes the transcriptions and required data to the data csv file

    Args:
        manifest_file (str): target path to main manifest file
        filepath (str): path to master json file containing all data
        transcription (str): transcribed string
        duration (int): duration of audio file
    """
    STRING = {"audio_filepath": f'"{filepath}"', "text": f'"{transcription}"', "duration": f'"{duration}"'}
    
    with open(manifest_file, "a+") as json_file:            
        json.dump(STRING, json_file)
        
def replacements(transcription: str):
    """ replacements changes short hand abbrevations of words back to original for transcription

    Args:
    transcription (str): Transcription to be checked for any abbreviations used
    """
    transcription = "1 2 3 4 5 oblique 6 7 8 9"
    replacements = {"o": "oblique", "a": "attention", "e": "end"}
    split_transcription = transcription.split()
    updated = []
    for index, part in enumerate(split_transcription):
        if part.lower() in replacements.keys():
            updated.append(replacements[part])
        else:
            updated.append(part)

    print(f"Original: {transcription}")
    print(f"With replacements: {' '.join(updated) }")
    
    return " ".join(updated)


def linux_to_windows(windows_dir: str, linux_dir: str):
    """ linux_to_windows converts windows directories to linux directories

    Args:
        windows_dir (str): old windows directory
        linux_dir (str): target linux directory        
    """
    file_path = windows_dir
    new_path = windows_dir + file_path[len(linux_dir):]

    print(f"Linux Path: {file_path}")
    print(f"Windows Path: {new_path}")  
    
def convert_paths(linux_folder: str):
    """ convert_paths modifies the old windows directory to the linux directory

    Args:
        linux_folder (str): target linux directory folder        
    """
    with open(linux_folder, "r") as f:
        contents = f.readlines()
        headings = contents[0]
        data = contents[1:]
    
    new_csv = [headings]
    print("a", new_csv)
    
    for row in data:
        split_row= row.split(",")
        path = split_row[0]
        file_name_orig = path.split("/")[-1]
        file_name_new = linux_folder +  "/" + file_name_orig
        new_row = ",".join([file_name_new, split_row[1], split_row[2]])
        print(new_row)
        new_csv.append(new_row)
    print(new_csv)

    with open("new_csv.csv", "w+") as f:
        for line in new_csv:
            f.write(line)

def json_split(input_file: str) -> None:
    """ json_split splits master file of all data into training, test and development

    Args:
        input_file (str): master csv file containing all transcripts data
    """
    # SPLIT POINTS - specify percentages of which each is used
    SPLITS: dict[str, float] = {"training": 0.8,
                                "validation": 0.2,}

    with open(input_file, "r") as csv_file:
        data = list(csv.reader(csv_file))
        headers = data[0]
        data = data[1:]

    # Randomise order of data
    random.shuffle(data)

    rows = len(data)
    i = 0
    for s in SPLITS:
        filename = os.path.dirname(input_file) + f"/{s}.csv"
        # Get required proportion of training data
        d = data[i:i+math.ceil(SPLITS[s]*rows)]
        i += len(d)
        write_data(filename, headers, d)


def write_data(output_file: str, header: list[str], data: list[any]) -> None:
    """ write_data writes the required header and data to a named csv file

    Args:
        input_file (str): where the file will be written
        header (list[str]): header for the csv data
        data (list[any]): transcript data to be copied
    """
    with open(output_file, "w+") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(data)

def menu() -> None:
    """ Menu for ANSL Transcription Tool
    
    Args:
    """
    print("Welcome to the ANSL Transcription Tool")

    choice = input("""
    A: Transcribe files in selected folder
    B: Split and shuffle data into two seperate datasets, training and validation
    C: Convert windows directory to linux directory for learning
    Q: Quit the ANSL Transcription Tool

Please enter your choice: """)

    print()

    root = Tk()
    root.overrideredirect(True)
    root.lift()
    root.attributes('-topmost',True)
    root.after_idle(root.attributes,'-topmost',False)
    

    if choice == "A" or choice == "a":
        transcribe_dir = askdirectory(title='Select Folder for transcribing data') # shows dialog box and return the path
        root.withdraw
        if transcribe_dir == "":
            print("Folder not selected, returning to main menu")
            menu()
        else:
            file_iterate(transcribe_dir)
            
    elif choice == "B" or choice == "b":
        split_dir = askdirectory(title='Select File for splitting and shuffling') # shows dialog box and return the path
        root.withraw()
        
        if split_dir == "":
            print("File not selected, returning to main menu")
            menu()
        else:
            json_split(split_dir)
        
    elif choice == "C" or choice == "c":
        linux_dir = askopenfilename(filetypes=[("JSON file","*.json")], title='Select Manifest file to convert directories')
        root.withdraw

        if linux_dir == "":
            print("File not selected, returning to main menu")
            menu()
        else:            
            convert_paths(linux_dir)
        
    elif choice == "Q" or choice == "q":
        sys.exit
        
    else:
        print("You must only select either A, B, C or Q")
        print("Please try again")
        menu()
    
menu()
