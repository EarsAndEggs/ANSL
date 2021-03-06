import os
import sys
import random
from typing import List
import numpy as np

import json
import codecs

import pydub
import simpleaudio

from natsort import natsorted

from tkinter import Tk
from tkinter.filedialog import askdirectory, askopenfilename

from num2words import num2words
from pydub import AudioSegment
from pydub import generators
from pydub import playback

def file_iterate(audio_dir: str) -> None:
    """ file_iterate goes over each mp3 file and provides the ability to transcribe them


    Args:
        audio_dir (str): directory that contains the audio clips to be transcribed
    """
    print("IMPORTANT: A Manifest file for transcription data MUST be selected or created before continuing! Before continuing, please create a manifest file for output while the program is paused. To continue, input any key: ")
    print("")
    
    tk = Tk()
    tk.overrideredirect(True)
    tk.lift()
    tk.attributes('-topmost',True)
    tk.after_idle(tk.attributes,'-topmost',False)
    
    processed_dir = audio_dir+"/processed"
    if not os.path.exists(processed_dir):
        os.makedirs(processed_dir)
        
    deleted_dir = audio_dir+"/deleted"
    if not os.path.exists(deleted_dir):
        os.makedirs(deleted_dir)
        
    manifest_path = askopenfilename(initialdir=f'"{audio_dir}"',filetypes=[("JSON file","*.json")], title='Select Manifest file')
    tk.withdraw

    if manifest_path == "":
        sys.exit("Manifest File was NOT selected, please make sure to create a manifest file for transcription before using this function. Stopping execution!")
    else:            

        audio_files = os.listdir(audio_dir)
        
        for audio_file in natsorted(audio_files):
            file_name = os.fsdecode(audio_file)
            if file_name.endswith(".wav"):
                #wav_import_number = len([True for audio_file in audio_files if audio_file.endswith(".wav")])
                wav_import_number = len([name for name in os.listdir(audio_dir) if os.path.isfile(os.path.join(audio_dir, name))])
                print(f"{wav_import_number} audio clips remaining for processing")

                file_path = os.path.abspath(os.path.join(audio_dir, file_name))
                processed_path = os.path.abspath(os.path.join(processed_dir, file_name))
                deleted_path = os.path.abspath(os.path.join(deleted_dir, file_name))
                
                sound1 = AudioSegment.from_file(file_path)
                sound2 = generators.Sine(freq=1000).to_audio_segment(duration=1000)
                sound3 = AudioSegment.silent(500)

                combinedsound = sound3 + sound1 + sound2
                #samples = combinedsound.get_array_of_samples()
                #samples = np.array(samples)
                
                audiofile = AudioSegment.from_wav(file_path)
                audio_duration = audiofile.duration_seconds
                
                print(f"Playing: {file_path} with: {audio_duration} seconds of data")


                #playback = simpleaudio.WaveObject(combinedsound.raw_data, num_channels=combinedsound.channels, bytes_per_sample=combinedsound.sample_width, sample_rate=combinedsound.frame_rate)
                play_obj = pydub.playback._play_with_simpleaudio(combinedsound*3)

                ans = input("Should this audio file be deleted? (y/n) ")

                play_obj.stop()
                while ans not in ('y', 'n','Y','N'):
                    ans = input("Invalid input, please type either (y/n)")
                
                if ans == "Y" or ans == "y":
                    os.rename(file_path,deleted_path)
                    print("Deleted " + file_path + ", moving on to next audio clip")
                    
                elif ans == "N" or ans == "n":
                    
                    play_obj = pydub.playback._play_with_simpleaudio(combinedsound*10)

                    input_transcription = input("Enter transcription: ")
                    play_obj.stop()
                    
                    cleaned_transcription = transcibe_num2word(input_transcription)
                    expanded_transcription = replacements(cleaned_transcription)
                    
                    print(expanded_transcription)
                    json_append(manifest_path,file_path,expanded_transcription,audio_duration)
                    
                    os.rename(file_path,processed_path)

                    print("Appended to manifest file, moving on to next audio clip")

    print("All files have now been processed! Please check the manifest file for any inconsistencies!")


def cut_audio(filecut: str, start: int, end: int, maxsecs = 10, steps = 0.1) -> None:
    
    valid = np.arange(0, maxsecs, steps).tolist()
    
    if start or end not in valid:
        raise ValueError("Error: start or end must range from 0 to %r." % maxsecs)
    
    sound_file = pydub.AudioSegment.from_wav(filecut)
    sound_file_Value = np.array(sound_file.get_array_of_samples())

    new_file=sound_file_Value[start : end]
    song = pydub.AudioSegment(new_file.tobytes(), frame_rate=sound_file.frame_rate,sample_width=sound_file.sample_width,channels=sound_file.channels)

    song.export(filecut, format="wav")

def gui_input(type: int, title: str) -> str:

    root = Tk()
    root.overrideredirect(True)
    root.lift()
    root.attributes('-topmost',True)
    root.after_idle(root.attributes,'-topmost',False)
    
    valid = {0, 1}
    if type not in valid:
        raise ValueError("Error: type must be one of %r." % valid)
    
    if type == 0:
        opendir = askdirectory(title=title)
        return opendir
    elif type == 1:
        openfilename = askopenfilename(filetypes=[("JSON file","*.json")], title=title)
        return openfilename
    

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
    STRING = {"audio_filepath": f"{filepath}", "text": f"{transcription}", "duration": duration}
        
    with open(manifest_file, "a") as json_file:            
        json_file.write(json.dumps(STRING)+'\n')
        json_file.close()
        
def replacements(transcription: str) -> str:
    """ replacements changes short hand abbrevations of words back to original for transcription

    Args:
    transcription (str): Transcription to be checked for any abbreviations used
    """
    replacements = {"o": "oblique", "a": "attention", "e": "out"}
    split_transcription = transcription.split()
    updated = []
    
    for index, part in enumerate(split_transcription):
        if part.lower() in replacements.keys():
            updated.append(replacements[part])
        else:
            updated.append(part)

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
    manifest_new_path = os.path.abspath(os.path.join(manifest_new_dir, "manifest_new.json"))
    
    if not os.path.exists(manifest_new_path):
        open(manifest_new_path, 'w').close()
    
    if convert_dir == "":
        sys.exit("Linux directory has not been selected! Stopping execution! Please restart the tool and try again.")
    else:
        new_file = open(manifest_new_path,'w')

        with codecs.open(manifest_file, 'r+', encoding='utf-8') as f:
            
            file_data = f.read()

            for line in file_data.splitlines():
                valid_json = f"[{line}]"
                json_data = json.loads(valid_json)
                
                for i in json_data:
                    json_filepath = i['audio_filepath']
                    json_filename = os.path.basename(json_filepath)
                    
                    final_path = os.path.abspath(os.path.join(convert_dir_fixed, json_filename))

                    i['audio_filepath'] = f'{final_path}'
                                        
                    new_file.write(json.dumps(json_data)+'\n'.strip('[]'))
                    
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

        train_data = data[:int((len(data)+1)*.80)]
        valid_data = data[int((len(data)+1)*.80):]
        
        print("Current weightings are set to: 80% - Training | 20% - Validation")
           
    with open(train_data_path, 'w') as train_f:
        for train_item in train_data:
            train_f.write("%s\n" % train_item)
    
    with open(valid_data_path, 'w') as valid_f:
        for valid_item in valid_data:
            valid_f.write("%s\n" % valid_item)
    
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