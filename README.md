# train_nlp
自然言語処理の練習


# directories
```
├── README.md
└── zoom_chat
    ├── data
    │   ├── input
    │   │   └── meeting_saved_chat.txt
    │   ├── output
    │   └── preprocess
    └── src
        ├── batch.sh
        └── main_co-occurrence_network.py
```

# zoom_chat
## 概要
zoomチャットのテキストを読み込んで解析する

## 前提
* カレントディレクトリはスクリプトが存在する場所

## バッチ処理
* 実行例
```
sh batch.sh "../data/input/meeting_saved_chat.txt" "../data/input/ng_list.txt" 70 2
```
* 実行内容
  * 共起ネットワーク図の作成スクリプトを実行
  * 〜スクリプトを実行

## 共起ネットワーク作成
* 実行例
```
    python3 main_co-occurrence_network.py \
        --path "../data/input/meeting_saved_chat.txt" \
        --ng_list_path "../data/input/ng_list.txt" \
        --n_word_max 70 \
        --th_lowest_cnt 2
```
* 実行内容
  * 共起ネットワーク作成、png出力。ランダム配置で10枚出す

## よくあるエラー
### ファイルパスにスペースが含まれていてエラーが出る場合
引数指定時にダブルクォーテーションでくくりましょう