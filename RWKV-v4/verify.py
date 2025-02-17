########################################################################################################
# The RWKV Language Model - https://github.com/BlinkDL/RWKV-LM
########################################################################################################

# this is for verifying the results of different models and make sure they agree with each other

import numpy as np
np.set_printoptions(precision=4, suppress=True, linewidth=200)

import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
os.environ['RWKV_FLOAT_MODE'] = 'fp16' # 'bf16' (stable) or 'fp16' (will overflow after training a large model for very long. can be solved in the future)
os.environ['RWKV_RUN_DEVICE'] = 'cuda'
RUN_DEVICE = os.environ['RWKV_RUN_DEVICE']

import torch
from src.model_run import RWKV_RNN, RWKV_GPT
from src.model import GPT, GPTConfig

TOKEN_MODE = 'pile' # char / pile

if TOKEN_MODE == 'char':
    MODEL_NAME = 'trained-1'
    WORD_NAME = 'vocab'         # the .json vocab (generated by train.py)
    ctx_len = 1024
    n_layer = 6
    n_embd = 512
    UNKNOWN_CHAR = ' '   # here we just set it to [space] for simplicity
elif TOKEN_MODE == 'pile':
    WORD_NAME = ['20B_tokenizer.json', '20B_tokenizer.json']
    MODEL_NAME = 'RWKV-4-Pile-169M-20220807-8023'
    ctx_len = 1024
    n_layer = 12
    n_embd = 768
    UNKNOWN_CHAR = None

model_type = 'RWKV'

from src.utils import TOKENIZER
tokenizer = TOKENIZER(WORD_NAME, UNKNOWN_CHAR=UNKNOWN_CHAR)
if TOKEN_MODE == 'pile':
    tokenizer.vocab_size = 50277

########################################################################################################

model_train = GPT(GPTConfig(tokenizer.vocab_size, ctx_len, model_type=model_type, n_layer=n_layer, n_embd=n_embd)).cuda()

if os.environ['RWKV_FLOAT_MODE'] == 'fp16':
    model_train = model_train.half()
elif os.environ['RWKV_FLOAT_MODE'] == 'bf16':
    model_train = model_train.bfloat16()

print('loading ' + MODEL_NAME)
m2 = torch.load(MODEL_NAME + '.pth', map_location=RUN_DEVICE)
model_train.load_state_dict(m2)

model_rnn = RWKV_RNN(MODEL_NAME, RUN_DEVICE, model_type, n_layer, n_embd, ctx_len)
model_gpt = RWKV_GPT(MODEL_NAME, RUN_DEVICE, model_type, tokenizer.vocab_size, n_layer, n_embd, ctx_len).cuda()

########################################################################################################

# context = '\nIn a'
context = '\nIn a shocking finding, scientist discovered a herd of dragons living in a remote, previously unexplored valley, in Tibet. Even more surprising to the researchers was the fact that the dragons spoke perfect Chinese.'

if TOKEN_MODE == 'char':
    ctx = [tokenizer.stoi.get(s, tokenizer.UNKNOWN_CHAR) for s in context]
elif TOKEN_MODE == 'pile':
    ctx = tokenizer.tokenizer.encode(context)
print(f'input len {len(ctx)} data {ctx}')

########################################################################################################

print('\nRWKV-GPT output')
out = model_gpt.forward(torch.tensor(ctx).unsqueeze(0).cuda())[0].detach().cpu().numpy()
print(out)

print('\nRWKV-RNN output')
model_rnn.clear()
src_len = len(ctx)
for i in range(src_len):
    x = ctx[:i+1]
    out = model_rnn.run(x)
    if i < 3 or i >= src_len - 3:
        print(torch.tensor(out).detach().cpu().numpy())
    if i == 2:
        print('...')

print('\nRWKV-train output')
out = model_train.forward(torch.tensor([ctx]).cuda())[0][0].detach().cpu().float().numpy()
print(out, '\n')
