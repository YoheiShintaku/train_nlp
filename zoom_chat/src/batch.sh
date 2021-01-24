#!/bin/bash
# 実行例: sh batch.sh ../data/input/meeting_saved_chat.txt 80
zoom_chat_path=$1
n_word_max=$2

# 共起ネットワーク図の作成スクリプトを実行
echo 'main_co-occurrence_network.py'
python3 main_co-occurrence_network.py --path $zoom_chat_path --n_word_max $n_word_max