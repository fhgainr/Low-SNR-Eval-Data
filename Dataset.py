import os
import random
import sys
import yaml
import librosa
import numpy as np
from audiolib import audioread, audiowrite, segmental_snr_mixer, activitydetector, is_clipped, add_clipping
import random
from argparse import ArgumentParser


random.seed(10)
np.random.seed(0)

def load_config(config_path):
    """Load the configuration file."""
    with open(config_path, "r") as yamlfile:
        return yaml.load(yamlfile, Loader=yaml.FullLoader)

def get_noise_files_by_category(noise_path, selected_categories):
    """
    Organize noise files into a dictionary by category.
    Each key corresponds to a category and its value is the list of files in that category.
    """
    return {cat: os.listdir(os.path.join(noise_path, cat)) for cat in selected_categories}

def load_audio(file_path, target_fs):
    """Load audio and resample to the target sampling rate if needed."""
    try:
        audio, fs = librosa.load(file_path, sr=None)
        if fs != target_fs:
            audio = librosa.resample(audio, orig_sr=fs, target_sr=target_fs)
        return audio
    except Exception as e:
        sys.stderr.write(f"Error loading audio file {file_path}: {e}\n")
        return None

def mix_with_noise(clean_audio, noise_audio, snr, hparams):
    """
    Mix clean and noise audio at a given SNR level.
    Ensures noise audio matches the length of the clean audio.
    Returns clean, noise, and mixed audio signals.
    """
    clean_length = len(clean_audio)
    noise_length = len(noise_audio)

    # Adjust noise audio length to match clean audio length
    if noise_length < clean_length:
        # Repeat noise to match length
        noise_audio = np.tile(noise_audio, int(np.ceil(clean_length / noise_length)))[:clean_length]
    elif noise_length > clean_length:
        # Truncate noise to match length
        noise_audio = noise_audio[:clean_length]

    # Mix clean and noise using the specified SNR
    return segmental_snr_mixer(
        params=hparams, clean=clean_audio, noise=noise_audio, snr=snr
    )


def save_audio_signals(file_paths, audio_signals, target_fs):
    """Save clean, noise, and mixed audio signals to the specified paths."""
    for i in range(len(audio_signals)):
        try:
            audiowrite(file_paths[i], audio_signals[i], target_fs)
        except Exception as e:
            sys.stderr.write(f"Error writing file {file_paths[i]}: {e}\n")

def process_clean_files(clean_files, noise_files_by_category, hparams, target_fs, samples_size):
    file_num = 0
    snr_levels = range(hparams['snr_lower'], hparams['snr_upper']+1) 
    total_snr_levels = len(snr_levels)
    total_samples = len(clean_files) * samples_size
    
    # Ensure an equal number of samples for each SNR level
    samples_per_snr = total_samples // total_snr_levels
    snr_values = np.repeat(snr_levels, samples_per_snr)
    
    # Shuffle the SNR values to randomize the order
    np.random.shuffle(snr_values)

    for clean_idx, clean_file in enumerate(clean_files):
        print(f"\nProcessing Clean File {clean_idx + 1}/{len(clean_files)}: {clean_file}")
        clean_audio = load_audio(os.path.join(hparams['speech_dir'], clean_file), target_fs)
        if clean_audio is None:
            continue

        # Ensure unique noise categories for each clean file
        selected_categories = random.sample(list(noise_files_by_category.keys()), samples_size)

        for i, category in enumerate(selected_categories):
            noise_file = random.choice(noise_files_by_category[category])
            noise_audio = load_audio(os.path.join(hparams['noise_dir'], category, noise_file), target_fs)
            if noise_audio is None:
                continue

            # Mix clean and noise at the selected SNR
            snr = snr_values[file_num]  # Assign SNR sequentially
            clean_snr, noise_snr, noisy_snr, target_level = mix_with_noise(clean_audio, noise_audio, snr, hparams)


            # Generate filenames and paths
            clean_name = clean_file.split('.wav')[0]
            noise_name = noise_file.split('.wav')[0]
            noisy_filename = (
                f"{clean_name}_*{noise_name}*_snr{snr}_tl{target_level}_cat*{category}*_fileid_{file_num}.wav"
            )
            clean_filename = f"clean_fileid_{file_num}.wav"
            noise_filename = f"noise_fileid_{file_num}.wav"

            file_paths = [
                os.path.join(hparams['noisyspeech_dir'], noisy_filename),
                os.path.join(hparams['clean_proc_dir'], clean_filename),
                os.path.join(hparams['noise_proc_dir'], noise_filename),
            ]

            audio_signals = [noisy_snr, clean_snr, noise_snr]
            save_audio_signals(file_paths, audio_signals, target_fs)

            file_num += 1


def main():
    # Parse command-line arguments
    parser = ArgumentParser()
    parser.add_argument('--config_path', type=str, default='./config.yml', help="Path to the configuration file")
    args = parser.parse_args()

    # Load configuration
    hparams = load_config(args.config_path)

    # Validate noise categories from the configuration file
    noise_path = hparams['noise_dir']
    selected_categories = hparams.get('noise_categories', [])
    print('Number of noise_categories:',len(selected_categories), selected_categories )
    if len(selected_categories) < hparams['samples_size']:
        sys.stderr.write(f"ERROR: At least {hparams['samples_size']} unique noise categories are required in the configuration file.\n")
        sys.exit(1)

    # Get noise files by category
    noise_files_by_category = get_noise_files_by_category(noise_path, selected_categories)

    # List clean files
    clean_files = os.listdir(hparams['speech_dir'])

    # Process clean files
    process_clean_files(
        clean_files=clean_files,
        noise_files_by_category=noise_files_by_category,
        hparams=hparams,
        target_fs=hparams['fs'],
        samples_size=hparams['samples_size']
    )

if __name__ == "__main__":
    main()


            
            
            
            
    



