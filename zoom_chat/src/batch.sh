#!/bin/bash

chat_path=$1
ng_list_path=$2
n_word_max=$3
th_lowest_cnt=$4

# 共起ネットワーク図の作成スクリプトを実行
echo 'main_co-occurrence_network.py'
python3 main_co-occurrence_network.py \
    --chat_path "$chat_path" \
    --ng_list_path $ng_list_path \
    --n_word_max $n_word_max \
    --th_lowest_cnt $th_lowest_cnt