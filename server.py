import torch
import traceback
import re

from flask import Flask
from flask import request
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Load our model and use cuda if available
model = GPT2LMHeadModel.from_pretrained('./model-3')
tokenizer = GPT2Tokenizer.from_pretrained('./model-3')
if torch.cuda.is_available():
    device = torch.device("cuda")

    print('There are %d GPU(s) available.' % torch.cuda.device_count())

    print('We will use the GPU:', torch.cuda.get_device_name(0))
    model.cuda()
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")
model.to(device)


def response(msg):
    global model, tokenizer
    output = ""
    prompt = "<|bos|>" + msg + "\n"
    promptlen = len(prompt) - 7

    generated = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0)
    generated = generated.to(device)
    maxlen = 300 + promptlen
    sample_outputs = model.generate(generated, do_sample=True, top_k=50, max_length=maxlen, top_p=0.95, temperature=0.9,
                                    num_return_sequences=1)

    for i, sample_output in enumerate(sample_outputs):
        output = tokenizer.decode(sample_output, skip_special_tokens=True)
        output = output[promptlen:]
    output = output.strip()
    if output:
        return output
    else:
        return response(msg)


def topten(msg):
    global model, tokenizer
    output = ""
    prompt = "<|bos|>" + msg + "\n"
    promptlen = len(prompt) - 7

    generated = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0)
    generated = generated.to(device)
    sample_outputs = model.generate(generated, do_sample=True, top_k=50, max_length=50, top_p=0.95, temperature=0.9,
                                    num_return_sequences=10)

    for i, sample_output in enumerate(sample_outputs):
        line = tokenizer.decode(sample_output, skip_special_tokens=True)
        line = line[promptlen:]
        line = re.sub(r"[0-9][\.)]{1,2}", "", line)
        line = line.replace("\n", " ")
        output += "\n" + str((i+1)) + ". " + line

    return output.strip()


def subvert():
    global model, tokenizer
    output = ""
    prompt = "<|bos|>I can't believe "

    generated = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0)
    generated = generated.to(device)
    sample_outputs = model.generate(generated, do_sample=True, top_k=50, max_length=300, top_p=0.95, temperature=0.9,
                                    num_return_sequences=1)

    for i, sample_output in enumerate(sample_outputs):
        output = tokenizer.decode(sample_output, skip_special_tokens=True)

    return output.strip()


# server
app = Flask(__name__)
app.debug = False


@app.route('/', methods=['GET'])
def request_message():
    raw_text = request.args.get("msg") and request.args.get("msg") or ""
    gentype = int(request.args.get("type") and request.args.get("type") or 1)

    result = ""
    try:
        if gentype == 3:
            result = subvert()
        elif gentype == 2:
            result = topten(raw_text)
        else:
            result = response(raw_text)

    except Exception as e:
        print("Error!")
        print(str(e))
        tb = traceback.format_exc()
        print(tb)

    return result, 200, {'Content-Type': 'application/json; charset=utf-8'}


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, threaded=False)
