import requests
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool
import shutil
import os
from bs4 import BeautifulSoup
import soundfile as sf
import string
import re
import num2words
from tqdm import tqdm
import soundfile
import librosa
import os
from pathlib import Path

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

data_dir = "dataset_dir"
audio_dir = data_dir + "/wavs"
download_threads = 64

temp_path = "temp_audio"
sampling_rate = 22050

blocklist = ["potato", "_ding_", "00_part1_entry-6", "_escape_"]
sources = ["https://theportalwiki.com/wiki/GLaDOS_voice_lines_(Portal)", "https://theportalwiki.com/wiki/GLaDOS_voice_lines_(Portal_2)", "https://theportalwiki.com/wiki/GLaDOS_voice_lines_(Other)"]

def resample_audio(input_file_path, output_path, target_sampling_rate=22050):
    if not input_file_path.endswith(".wav"):
        raise NotImplementedError("Loading only implemented for wav files.")
    if not os.path.exists(input_file_path):
        raise FileNotFoundError(f"Cannot file input file at {input_file_path}")
    audio, sampling_rate = librosa.load(
      input_file_path,
      sr=target_sampling_rate
    )

    soundfile.write(
        output_path,
        audio,
        samplerate=target_sampling_rate,
        format="wav"
    )

def prep(args, overwrite=True):
    already_exists = os.path.exists(audio_dir)
    
    if already_exists and not overwrite:
        print("Data already downloaded")
        return
    
    if already_exists:
        print("Deleting previously downloaded audio")
        shutil.rmtree(audio_dir)
        
        if os.path.exists(temp_path):
            shutil.rmtree(temp_path)
    
    path = Path(audio_dir)
    path.mkdir(parents=True)

    download_parallel(args)

def remove_punctuation(str):
    return str.translate(str.maketrans('', '', string.punctuation))
    
def audio_duration(fn):
    f = sf.SoundFile(fn)
    return f.frames / f.samplerate

def download_file(args):
    url, filename = args[0], args[1]

    try:
        response = requests.get(url, allow_redirects=False)

        open(os.path.join(audio_dir, filename), "wb").write(response.content)
        return filename, True
    except:
        return filename, False

def download_parallel(args):
    results = ThreadPool(download_threads).imap_unordered(download_file, args)
    for result in results:
        if result[1]:
            print(bcolors.OKGREEN + "[" + u'\u2713' + "] " + bcolors.ENDC + result[0])
        else:
            print(bcolors.FAIL + "[" + u'\u2715' + "] " + bcolors.ENDC + result[0])

def main():
    urls = []
    filenames = []
    texts = []

    for s in sources:
        r = requests.get(s, allow_redirects=False)
    
        soup = BeautifulSoup(r.text.encode('utf-8').decode('ascii', 'ignore'), 'html.parser')
        for link_item in soup.find_all('a'):
            url = link_item.get("href", None)
            if url:
                if "https:" in url and ".wav" in url:
                    list_item = link_item.find_parent("li")
                    ital_item = list_item.find_all('i')
                    if ital_item:
                        text = ital_item[0].text
                        text = text.replace('"', '')
                        filename = url[url.rindex("/")+1:]
    
                        if "[" not in text and "]" not in text and "$" not in text:
                            if url not in urls:
                                for s in blocklist:
                                    if s in url:
                                        break
                                else:
                                    urls.append(url)
                                    filenames.append(filename)
                                    text = text.replace('*', '')
                                    texts.append(text)

    print("Found " + str(len(urls)) + " urls")

    args = zip(urls, filenames)

    prep(args)
    
    total_audio_time = 0
    outFile=open(os.path.join(data_dir, "manifest.csv"), 'w')
    for i in range(len(urls)):
        item = {}
        text = texts[i]
        filename = filenames[i]
        text = re.sub(r"(\d+)", lambda x: num2words.num2words(int(x.group(0))), text)

        total_audio_time = total_audio_time + audio_duration(os.path.join(audio_dir, filename))
        outFile.write(filename[:-4] + "|" + text + "\n")
 
    outFile.close()
    print("\n" + str(total_audio_time/60.0) + " min\n")

    shutil.copytree(audio_dir, temp_path)

    print("Resampling Audio...")
    for filename in tqdm(os.listdir(temp_path)):
        if ".wav" in filename:
            source_name = os.path.join(temp_path, filename)
            destination_name = os.path.join(audio_dir, filename)
            resample_audio(source_name, destination_name, target_sampling_rate=sampling_rate)
            
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)

main()