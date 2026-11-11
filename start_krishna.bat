@echo off
cd /d D:\krishna
call venv\Scripts\activate

set HF_HOME=D:\krishna\hf_cache
set HUGGINGFACE_HUB_CACHE=D:\krishna\hf_cache\hub
set HF_HUB_DISABLE_SYMLINKS_WARNING=1

python -m desktop.continuous_mode