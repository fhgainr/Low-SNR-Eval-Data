# Low-SNR Evaluation Data Generation

This repository provides scripts to generate low-SNR evaluation datasets for speech enhancement, as described in  
[*Leveraging Discriminative Latent Representations for Conditioning GAN-Based Speech Enhancement*](https://arxiv.org/abs/2508.20859).

---


## Setup

We use Conda to manage Python dependencies. Run the following commands to create and activate the environment:

```shell
conda env create -f environment_objective.yml
conda activate discogan_eval
```



### Step 1: Download the ESC-50 dataset
We use the ESC-50 dataset as the noise sources for creating our evaluation dataset.

```shell
$ cd low-snr-evaldata-generation 
$ git clone https://github.com/karolpiczak/ESC-50.git
```

### Step 2: Download DNS Challenge 2020 Test Set Clean signals
We use the DNS Challenge 2020 Non-reverberant Test Set Clean signals for creating our evaluation dataset.
Use the following link to download the clean signals

```shell
https://github.com/microsoft/DNS-Challenge/tree/interspeech2020/master/datasets/test_set/synthetic/no_reverb/clean
```
### Step 3: Organize the ESC-50 audio files by noise category
We re-organize the noise files from ESC-50 dataset by noise categories

```shell
$ python organize_files.py --csv_file './ESC-50-master/esc50.csv' --source_directory './ESC-50-master/audio' --destination_directory './noise_categories'
```

### Step 4: Create the evaluation dataset
First change the parameterization in the config.yml file and then run:

```shell
$ python dataset.py --config_path './config.yml' 
```







**Software Copyright License for Academic Use of the Fraunhofer Software, Version 1.0**  
(c) 2025 Fraunhofer-Gesellschaft zur Förderung der angewandten Forschung e.V.
