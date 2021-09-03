import torch
import traceback
import re
from aiohttp import web

from transformers import GPTNeoForCausalLM, GPT2Tokenizer

routes = web.RouteTableDef()

# Load our model and use cuda if available
model = GPTNeoForCausalLM.from_pretrained('./model-8')
tokenizer = GPT2Tokenizer.from_pretrained('./model-8')
if torch.cuda.is_available():
    device = torch.device("cuda")

    print('There are %d GPU(s) available.' % torch.cuda.device_count())

    print('We will use the GPU:', torch.cuda.get_device_name(0))
    model.cuda()
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")
model.to(device)
p = re.compile(r'<\|bos\|>((?s:.)*?)<\|eos\|>', re.IGNORECASE)
p2 = re.compile(r'.*reasons?(.*)', re.IGNORECASE)


def response(msg):
    global model, tokenizer, p
    output = ""
    prompt = "<|bos|>" + msg
    promptlen = len(msg)-1

    generated = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0)
    generated = generated.to(device)
    maxlen = 300 + promptlen
    sample_outputs = model.generate(generated, do_sample=True, top_k=200, max_length=maxlen, top_p=0.95, temperature=0.9,
                                    num_return_sequences=1)

    for i, sample_output in enumerate(sample_outputs):
        output = tokenizer.decode(sample_output, skip_special_tokens=False)
        m = re.match(p, output)
        if m:
            output = m.group(1)
        else:
            output = None

    if output:
        output = output.strip()
        return output[promptlen:]
    else:
        return response(msg)


def topten(msg):
    global model, tokenizer, p2
    output = ""

    msg = re.search(p2, msg).group(1)

    prompt = "<|bos|>" + msg
    promptlen = len(msg)
    maxlen = 200 + promptlen

    generated = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0)
    generated = generated.to(device)
    sample_outputs = model.generate(generated, do_sample=True, top_k=100, max_length=maxlen, top_p=0.95, temperature=0.9,
                                    num_return_sequences=30)

    _counter = 1
    for i, sample_output in enumerate(sample_outputs):
        if _counter > 10:
            break
        line = tokenizer.decode(sample_output, skip_special_tokens=False)
        m = re.match(p, line)
        if m:
            line = m.group(1)
            line = line[promptlen:]
            line = re.sub(r"[0-9][\.)]{1,2}", "", line)
            line = line.replace("\n", " ")
            line = line.strip()
            if line:
                output += "\n" + str((_counter)) + ". " + line
                _counter += 1
            else:
                continue

    return output.strip()


def subvert():
    global model, tokenizer
    output = ""
    prompt = "<|bos|>I can't believe "

    generated = torch.tensor(tokenizer.encode(prompt)).unsqueeze(0)
    generated = generated.to(device)
    sample_outputs = model.generate(generated, do_sample=True, top_k=200, max_length=100, top_p=0.95, temperature=0.8,
                                    num_return_sequences=1)

    for i, sample_output in enumerate(sample_outputs):
        output = tokenizer.decode(sample_output, skip_special_tokens=False)
        m = re.match(p, output)
        if m:
            output = m.group(1)
        else:
            output = 'Snape Kills Makima'

    return output.strip()


@routes.get('/')
async def request_message(request):
    raw_text = request.rel_url.query['msg'] or ""
    gentype = int(request.rel_url.query['type'] or 1)

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

    return web.Response(text=result)

if __name__ == '__main__':
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app)
