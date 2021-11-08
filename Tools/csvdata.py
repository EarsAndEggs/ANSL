import os
import sys
import csv
import math
import random
import json
import codecs

from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename

from num2words import num2words
from pydub import AudioSegment
from pydub.playback import play

def file_iterate(audio_dir: str) -> None:
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
    STRING = {"audio_filepath": f'"{filepath}"', "text": f'"{transcription}"', "duration": f'{duration}'}
    
    with open(manifest_file, "a+") as json_file:            
        json.dump(STRING, json_file)
        
def replacements(transcription: str) -> str:
    """ replacements changes short hand abbrevations of words back to original for transcription

    Args:
    transcription (str): Transcription to be checked for any abbreviations used
    """
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
    
def convert_paths(manifest_file: str) -> None:
    """ convert_paths modifies the old windows directory to the linux directory

    Args:
        manifest_file (str): target manifest file
    """
    ctk = Tk()
    ctk.overrideredirect(True)
    ctk.lift()
    ctk.attributes('-topmost',True)
    ctk.after_idle(ctk.attributes,'-topmost',False)
    
    convert_dir = askdirectory(title='Select Folder for final conversion directory')
    convert_dir_fixed = os.path.dirname(convert_dir)
    ctk.withdraw
    
    manifest_new_dir = os.path.dirname(manifest_file)
    manifest_new_path = os.path.join(manifest_new_dir, "manifest_new.json")
    
    if not os.path.exists(manifest_new_path):
        open(manifest_new_path, 'w').close()
    
    if convert_dir == "":
        sys.exit("Linux directory has not been selected! Stopping execution! Please restart the tool and try again.")
    else:
        new_file = open(manifest_new_path,'w')

        with codecs.open(manifest_file, 'r+', encoding='utf-8') as f:
            
            file_data = f.read()

            for line in file_data.splitlines():
                valid_json = "[{0}]".format(line)
                json_data = json.loads(valid_json)
                
                for i in json_data:
                    json_filepath = i['audio_filepath']
                    json_filename = os.path.basename(json_filepath)
                    
                    final_path = os.path.abspath(os.path.join(convert_dir_fixed, json_filename))

                    i['audio_filepath'] = f'{final_path}'
                                        
                    new_file.write(json.dumps(json_data).strip('[]'))
                    new_file.write('\n')
                    
        new_file.close
        print(f'"Finished conversion. Output in: {manifest_new_path}"')

def json_split(input_file: str) -> None:
    """ json_split splits master file of all data into training, test and development

    Args:
        input_file (str): master csv file containing all transcripts data
    """
    data_dir = os.path.dirname(input_file)
    
    train_data_path = os.path.abspath(os.path.join(data_dir, "training_manifest.json"))
    if not os.path.exists(train_data_path):
        open(train_data_path, 'w').close()
        
    valid_data_path = os.path.abspath(os.path.join(data_dir, "validation_manifest.json"))
    if not os.path.exists(valid_data_path):
        open(valid_data_path, 'w').close()
        
    with open(input_file, "rb") as f:
        data = f.read().split('\n')

        random.shuffle(data)

        train_data = data[:80]
        valid_data = data[20:]
        
        print("Current weightings are set to: 80% - Training | 20% - Validation")
           
    with open(train_data_path, 'w') as f:
        for train_item in train_data:
            f.write("%s\n" % train_item)
    
    with open(valid_data_path, 'w') as f:
        for valid_item in valid_data:
            f.write("%s\n" % valid_item)
    
    print("Splitting process complete!")
    print(f'"Output for training manifest in: {train_data_path}"')
    print(f'"Output for validation manifest in: {valid_data_path}"')

    
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
        split_dir = askopenfilename(filetypes=[("JSON file","*.json")], title='Select Manifest file to split into training and validation dataset manifests') # shows dialog box and return the path
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
