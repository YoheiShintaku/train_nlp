<!-- TOC -->

- [リポジトリ概要](#%E3%83%AA%E3%83%9D%E3%82%B8%E3%83%88%E3%83%AA%E6%A6%82%E8%A6%81)
- [zoom_chat](#zoom_chat)
    - [directories](#directories)
    - [HOW TO USE](#how-to-use)
        - [前提](#%E5%89%8D%E6%8F%90)
        - [共起ネットワーク作成](#%E5%85%B1%E8%B5%B7%E3%83%8D%E3%83%83%E3%83%88%E3%83%AF%E3%83%BC%E3%82%AF%E4%BD%9C%E6%88%90)
        - [バッチ処理](#%E3%83%90%E3%83%83%E3%83%81%E5%87%A6%E7%90%86)
    - [よくあるエラー](#%E3%82%88%E3%81%8F%E3%81%82%E3%82%8B%E3%82%A8%E3%83%A9%E3%83%BC)
        - [ファイルパスにスペースが含まれていてエラーが出る場合](#%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E3%83%91%E3%82%B9%E3%81%AB%E3%82%B9%E3%83%9A%E3%83%BC%E3%82%B9%E3%81%8C%E5%90%AB%E3%81%BE%E3%82%8C%E3%81%A6%E3%81%84%E3%81%A6%E3%82%A8%E3%83%A9%E3%83%BC%E3%81%8C%E5%87%BA%E3%82%8B%E5%A0%B4%E5%90%88)

<!-- /TOC -->

# リポジトリ概要
- 自然言語処理の練習
  - zoom_chat: zoomチャット解析

# zoom_chat
## directories
```
└── zoom_chat
    ├── data
    │   ├── output
    │   └── preprocess
    └── src
        ├── batch.sh
        └── main_co-occurrence_network.py
```

## HOW TO USE
### 前提
* カレントディレクトリはスクリプトが存在する場所

### 共起ネットワーク作成
* 実行例
```
    python3 main_co-occurrence_network.py \
        --chat_path "../data/input/meeting_saved_chat.txt" \
        --ng_list_path "../data/input/ng_list.txt" \
        --n_word_max 70 \
        --th_lowest_cnt 2
```

### バッチ処理
* 実行例
```
sh batch.sh "../data/input/meeting_saved_chat.txt" "../data/input/ng_list.txt" 65 2
```
* 実行内容
  * 共起ネットワーク図の作成スクリプトを実行
  * 〜スクリプトを実行

## よくあるエラー
### ファイルパスにスペースが含まれていてエラーが出る場合
引数指定時にダブルクォーテーションでくくりましょう