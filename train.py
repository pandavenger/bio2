import datetime
import json
import numpy as np
import random
import time
import torch

from torch.utils.data import Dataset, DataLoader, RandomSampler, SequentialSampler
from torch.utils.data import random_split
from transformers import GPT2LMHeadModel, GPT2Tokenizer, GPT2Config
from transformers import AdamW
from transformers import Trainer, TrainingArguments
from transformers import get_linear_schedule_with_warmup

bs = 2
pretrained_model = 'gpt2-medium'

# Now we'll create a list to iterate through.
with open('data/quotes_raw.json') as json_file:
    data = json.load(json_file)

quotes = []
for i in data:
    text = i['text']
    if len(text) < 512:
        quotes.append(text)

gpt2tokenizer = GPT2Tokenizer.from_pretrained(pretrained_model,
                                              bos_token='<|bos|>',
                                              eos_token='<|eos|>',
                                              pad_token='<|pad|>')

max_len = max([len(gpt2tokenizer.encode(quote)) for quote in quotes])

print(f'The longest quote text is {max_len} tokens long.')

class QuoteDataset(Dataset):

    def __init__(self, txt_list, tokenizer, gpt2_type=pretrained_model, max_length=max_len):
        self.tokenizer = tokenizer  # the gpt2 tokenizer we instantiated
        self.input_ids = []
        self.attn_masks = []

        for txt in txt_list:
            """
            This loop will iterate through each entry in the flavour text corpus.
            For each bit of text it will prepend it with the start of text token,
            then append the end of text token and pad to the maximum length with the 
            pad token. 
            """

            encodings_dict = tokenizer('<|bos|>' + txt + '<|eos|>',
                                       truncation=True,
                                       max_length=max_length,
                                       padding="max_length")

            """
            Each iteration then appends either the encoded tensor to a list,
            or the attention mask for that encoding to a list. The attention mask is
            a binary list of 1's or 0's which determine whether the langauge model
            should take that token into consideration or not. 
            """
            self.input_ids.append(torch.tensor(encodings_dict['input_ids']))
            self.attn_masks.append(torch.tensor(encodings_dict['attention_mask']))

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return self.input_ids[idx], self.attn_masks[idx]


dataset = QuoteDataset(quotes, gpt2tokenizer, max_length=max_len)

# Split into training and validation sets
train_size = int(0.9 * len(dataset))
val_size = len(dataset) - train_size

train_dataset, val_dataset = random_split(dataset, [train_size, val_size])

print(f'There are {train_size} samples for training, and {val_size} samples for validation testing')

print(dataset[0])

train_dataloader = DataLoader(
    train_dataset,
    sampler=RandomSampler(train_dataset),  # Sampling for training is random
    batch_size=bs
)

validation_dataloader = DataLoader(
    val_dataset,
    sampler=SequentialSampler(val_dataset),  # Sampling for validation is sequential as the order doesn't matter.
    batch_size=bs
)

configuration = GPT2Config.from_pretrained(pretrained_model, output_hidden_states=False)

model = GPT2LMHeadModel.from_pretrained(pretrained_model, config=configuration)
model.resize_token_embeddings(len(gpt2tokenizer))

if torch.cuda.is_available():

    # Tell PyTorch to use the GPU.
    device = torch.device("cuda")

    print('There are %d GPU(s) available.' % torch.cuda.device_count())

    print('We will use the GPU:', torch.cuda.get_device_name(0))
    model.cuda()

# If not...
else:
    print('No GPU available, using the CPU instead.')
    device = torch.device("cpu")

seed_val = 883

random.seed(seed_val)
np.random.seed(seed_val)
torch.manual_seed(seed_val)
torch.cuda.manual_seed_all(seed_val)

epochs = 4
warmup_steps = 1e2
sample_every = 100

optimizer = AdamW(model.parameters(),
                  lr=8e-4,
                  eps=1e-8
                  )

total_steps = len(train_dataloader) * epochs
scheduler = get_linear_schedule_with_warmup(optimizer,
                                            num_warmup_steps=warmup_steps,
                                            num_training_steps=total_steps)


def format_time(elapsed):
    return str(datetime.timedelta(seconds=int(round((elapsed)))))


total_t0 = time.time()

training_stats = []

model = model.to(device)

for epoch_i in range(0, epochs):

    print(f'Beginning epoch {epoch_i + 1} of {epochs}')

    t0 = time.time()

    total_train_loss = 0

    model.train()

    for step, batch in enumerate(train_dataloader):

        b_input_ids = batch[0].to(device)
        b_labels = batch[0].to(device)
        b_masks = batch[1].to(device)

        model.zero_grad()

        outputs = model(b_input_ids,
                        labels=b_labels,
                        attention_mask=b_masks,
                        token_type_ids=None
                        )

        loss = outputs[0]

        batch_loss = loss.item()
        total_train_loss += batch_loss

        # Get sample every 100 batches.
        if step % sample_every == 0 and not step == 0:

            elapsed = format_time(time.time() - t0)
            print(f'Batch {step} of {len(train_dataloader)}. Loss:{batch_loss}. Time:{elapsed}')

            model.eval()

            prompt = "<|bos|>"

            generated = torch.tensor(gpt2tokenizer.encode(prompt)).unsqueeze(0)
            generated = generated.to(device)

            sample_outputs = model.generate(
                generated,
                do_sample=True,
                top_k=50,
                max_length=200,
                top_p=0.95,
                num_return_sequences=1
            )
            for i, sample_output in enumerate(sample_outputs):
                print(f'Example output: {gpt2tokenizer.decode(sample_output, skip_special_tokens=True)}')

            model.train()

        loss.backward()

        optimizer.step()

        scheduler.step()

    # Calculate the average loss over all of the batches.
    avg_train_loss = total_train_loss / len(train_dataloader)

    # Measure how long this epoch took.
    training_time = format_time(time.time() - t0)

    print(f'Average Training Loss: {avg_train_loss}. Epoch time: {training_time}')

    t0 = time.time()

    model.eval()

    total_eval_loss = 0
    nb_eval_steps = 0

    # Evaluate data for one epoch
    for batch in validation_dataloader:
        b_input_ids = batch[0].to(device)
        b_labels = batch[0].to(device)
        b_masks = batch[1].to(device)

        with torch.no_grad():
            outputs = model(b_input_ids,
                            attention_mask=b_masks,
                            labels=b_labels)

            loss = outputs[0]

        batch_loss = loss.item()
        total_eval_loss += batch_loss

    avg_val_loss = total_eval_loss / len(validation_dataloader)

    validation_time = format_time(time.time() - t0)

    print(f'Validation loss: {avg_val_loss}. Validation Time: {validation_time}')

    # Record all statistics from this epoch.
    training_stats.append(
        {
            'epoch': epoch_i + 1,
            'Training Loss': avg_train_loss,
            'Valid. Loss': avg_val_loss,
            'Training Time': training_time,
            'Validation Time': validation_time
        }
    )

print(f'Total training took {format_time(time.time() - total_t0)}')

output_dir = './model'

# Save a trained model, configuration and tokenizer using `save_pretrained()`.
# They can then be reloaded using `from_pretrained()`
model_to_save = model.module if hasattr(model, 'module') else model
model_to_save.save_pretrained(output_dir)
gpt2tokenizer.save_pretrained(output_dir)
# torch.save(args, os.path.join(output_dir, 'training_args.bin'))

model.eval()

prompt = "<|bos|>"

generated = torch.tensor(gpt2tokenizer.encode(prompt)).unsqueeze(0)
generated = generated.to(device)

sample_outputs = model.generate(
    generated,
    do_sample=True,
    top_k=50,
    max_length=300,
    top_p=0.95,
    num_return_sequences=10
)

for i, sample_output in enumerate(sample_outputs):
    print("{}: {}\n\n".format(i, gpt2tokenizer.decode(sample_output, skip_special_tokens=True)))
