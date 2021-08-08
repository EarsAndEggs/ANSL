import os
import sys
import csv
import math
import random

from num2words import num2words
from pydub import AudioSegment
from pydub.playback import play

def file_iterate(audio_dir: str):
    """ file_iterate goes over each mp3 file and provides the ability to transcribe them


    Args:
        audio_dir (str): directory that contains the audio clips to be transcribed
    """
    print(audio_dir)
    output_dir = audio_dir+"/processed"
    print(output_dir)

    files = os.listdir(audio_dir)
    for file in files:
        filename = os.fsdecode(file)
        if filename.endswith(".mp3"):

            wav_import_number = len([True for file in files if file.endswith(".mp3")])
            print(f"{wav_import_number} audio clips remaining for processing")

            file_path = os.path.join(audio_dir, filename)
            file_size = os.path.getsize(file_path)
            print(f"Playing: {file_path} with: {file_size} bytes of data")

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

                    csv_append(file_path, file_size, cleaned_transcription)

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


def csv_append(filepath: str, wav_path: str, bytes: int, transcription: str) -> None:
    """ csv_append writes the transcriptions and required data to the data csv file

    Args:
        filepath (str): path to master csv file containing all data
        wav_path (str): path to audio file
        bytes (int): size of audio file in bytes
        transcription (str): transribed string
    """
    HEADER = ["wav_filename", "wav_size", "transcript"]
    exsists = os.path.exists(filepath)
    with open(filepath, "a+") as csv_file:
        writer = csv.writer(csv_file)
        # If file is new write headers to top row
        if not exsists:
            writer.writerow(HEADER)
        writer.writerow([wav_path, bytes, transcription])


def csv_split(input_file: str) -> None:
    """ csv_split splits master file of all data into training, test and development

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
