# use for RWKV Reqs instalation
wget https://data.deepai.org/enwik8.zip
unzip ./enwik8.zip
mkdir data && mv enwik8 ./data/
rm enwik8.zip
pip install torch==1.13.1+cu117 torchvision==0.14.1+cu117 torchtext==0.14.1 torchaudio==0.13.1 torchdata==0.5.1 --extra-index-url https://download.pytorch.org/whl/cu117
pip install pytorch-lightning==1.9.2
pip install deepspeed==0.7.0
pip install tokenizers
pip install prompt_toolkit

cp RWKV-LM/RWKV-v4/cuda .