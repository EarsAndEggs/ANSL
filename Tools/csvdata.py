import os
import sys
import csv
import math
import random
import json

from num2words import num2words
from pydub import AudioSegment
from pydub.playback import play

def file_iterate(audio_dir: str):
    """ file_iterate goes over each mp3 file and provides the ability to transcribe them


    Args:
        audio_dir (str): directory that contains the audio clips to be transcribed
    """
    print(audio_dir)
    output_dir = audio_dir+"\processed"
    print(output_dir)

    files = os.listdir(audio_dir)
    for file in files:
        filename = os.fsdecode(file)
        if filename.endswith(".wav"):

            wav_import_number = len([True for file in files if file.endswith(".wav")])
            print(f"{wav_import_number} audio clips remaining for processing")

            file_path = os.path.join(audio_dir, filename)
            
            audiofile = AudioSegment.from_file(file_path)
            audio_duration = audiofile.duration_seconds
            
            print(f"Playing: {file_path} with: {audio} seconds of data")

            play_audio = True
            while play_audio:
                audio = AudioSegment.from_mp3(file_path)
                play(audio)

                input_transcription = input("Enter transcription: ")
                choice = input("Repeat audio clip? (y/n) ")

                while choice.lower() not in ('y', 'n'):
                    choice = input("Invalid input, please type either (y/n)")

                if choice == 'y':
                    print("Repeating audio clip")
                elif choice == 'n':
                    play_audio = False
                    cleaned_transcription = transcibe_num2word(input_transcription)
                    print(cleaned_transcription)

                    json_append(file_path,cleaned_transcription,audio_duration)

                    print("Moving on to next audio clip")
                    break

    print("Finished transcription")


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


def json_append(filepath: str, transcription: str, duration: int) -> None:
    """ json_append writes the transcriptions and required data to the data csv file

    Args:
        filepath (str): path to master json file containing all data
        transcription (str): transcribed string
        duration (int): duration of audio file
    """
    STRING = {"audio_filepath": f'"{filepath}"', "text": f'"{transcription}"', "duration": f'"{duration}"'}

    #exsists = os.path.exists(filepath)
    
    with open(filepath, "a+") as json_file:
        # If file is new write headers to top row
        #if not exsists:
            
        json.dump(STRING, json_file)
        
def remove_clips():
    """ remove_clips deletes file if not suitable for transcription

    Args:
    """
    audio_files = os.listdir("audio_files")
    for f in audio_files:
        print(f)
        # transcribe_audio(f)
        transcribed_file = "EXAMPLE. INPUT WOULD COME FROM TRANSCRIBE FUNCTION"
        print(transcribed_file)
        ans = input("Do you want this file to be transcribed? Y/N ")
        if ans.lower() == "n":
            os.rename("./audio_files/"+f,"./bad_files/"+f)
        else:
            # play transcription to check accuracy
            pass
    print("Files that you said N to, are now in a new folder")

def replacements():
    """ replacements changes short hand abbrevations of words back to original for transcription

    Args:
    """
    transcription = "1 2 3 4 5 oblique 6 7 8 9"
    replacements = {"oblique": "o"}
    split_transcription = transcription.split()
    updated = []
    for index, part in enumerate(split_transcription):
        if part.lower() in replacements.keys():
            updated.append(replacements[part])
        else:
            updated.append(part)

    print(f"Original: {transcription}")
    print(f"With replacements: {' '.join(updated) }")


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
    SPLITS: dict[str, float] = {"training": 0.7,
                                "test": 0.2,
                                "dev": 0.1}

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


if __name__ == "__main__":
    if len(sys.argv) < 2:
        file_path = os.getcwd()
    else:
        file_path = sys.argv[1]
    file_iterate(file_path)
