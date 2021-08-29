# bio2
*TODO: Actually flesh this README file out*

A gross little discord bot based in Python for private use with various entertainment functions, notably GPT2 conversation and text generation

Models I am using were trained on an RTX 3080 running CUDA 10.2 with tensorflow 2.4 and pytorch 1.8
Bot has been tested in the following environment(s):
- Windows 10 Pro
  - RTX 3080
  - tensorflow 2.3
  - torch 1.7.1
  - CUDA 10.0
- Ubuntu 20.04
  - RTX 1070
  - tensorflow 2.3
  - torch 1.7.1
  - CUDA 10.1

# Operation Instructions (barebones atm)
- refer to `requirements.txt` for python library installation
- `train.py` looks for training data at `data/quotes_raw.json`
  - json data must be an array of json objects with a parameter `text` containing each phrase
- existing models or the model generated from `train.py` must be placed the `model` folder
- using `config.example.py` and `data.example.json`, create `config.py` and `data.json`
  - you must provide your own api keys
- for full operation `server.py` and `bio2.py` should both be running

# Notable Features
 - Solves the issue of ML text generation by running a local server instance
 - Using an action queue to avoid too many parallel operations
 - Ease of source location though a single reaction, reducing redundancy
 - Various inappropriate injokes
