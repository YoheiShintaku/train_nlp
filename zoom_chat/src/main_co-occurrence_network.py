# coding: utf-8
'''
前提
    カレントディレクトリは本スクリプトのある場所
実行例
    python3 main_co-occurrence_network.py --path ../data/input/meeting_saved_chat.txt --n_word_max 50
'''
import pandas as pd
import numpy as np
import itertools
from collections import Counter
import MeCab
import re
import argparse
import matplotlib.pyplot as plt
import japanize_matplotlib
import networkx as nx

# input columns
TIME_COLUMN = 'time'
TEXT_ORG_COLUMN = 'text_org'
# add columns
NAME_COLUMN = 'name' 
TEXT_COLUMN = 'text'
WORD_LIST_COLUMN = 'word_list'

def main(path: str, n_word_max: int) -> None:
    '''
    debug用
        path = '../data/input/meeting_saved_chat.txt'
        n_word_max = 80
    '''

    df_chat = load(path)

    df_chat = preprocess(df_chat)

    # 発言内容の単語リストを取得し、その列を追加
    df_chat[WORD_LIST_COLUMN] = get_word_list(df_chat[TEXT_COLUMN])

    # 名前から生じる単語リストを取得し、NGワードとする
    ng_list = get_word_in_name(get_word_list(df_chat[NAME_COLUMN]))

    # 
    plot_network(df_chat[WORD_LIST_COLUMN], ng_list, 
        th_lowest_cnt=2, n_word_max=n_word_max,)

    return None


def load(path: str) -> pd.DataFrame:
    '''
    '''
    names = [TIME_COLUMN, TEXT_ORG_COLUMN]
    df = pd.read_csv(path, sep='\t', header=None, names=names)
    print(path, df.shape)
    return df


def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    '''
    '''
    def _apply_func_get_name(x):
        '''
        debug用
            x = df_chat[TEXT_ORG_COLUMN].values[0]
        '''
        name = str(x).split(':')[0].split(' ')[2]
        return name

    def _apply_func_get_contents(x):
        '''
        概要
            発言者:発言内容から、発言内容を取得
        debug用
            x = df_chat[TEXT_ORG_COLUMN].values[0]
        '''
        contents = str(x).split(':')[1]
        return contents

    df = df.dropna(subset=[TEXT_ORG_COLUMN] ,axis=0)  # 発言内容の欠損行を除外
    df = df.assign(**{
        TEXT_COLUMN: df[TEXT_ORG_COLUMN].apply(_apply_func_get_contents).copy(),
        NAME_COLUMN: df[TEXT_ORG_COLUMN].apply(_apply_func_get_name).copy(),
        })  # warning messageがうざいのでassignを使う
    return df
    

def get_word_list(sr:pd.Series) -> pd.Series:
    '''
    debug用
        sr = df[TEXT_COLUMN]
    '''
    def _judge(s:str) -> bool:
        '''
        正規表現で指定した品詞にマッチすればTrue
        '''
        return cmp.match(s) is not None

    def _apply_func_get_word_list(s):
        '''
        # debug用
        s = '皆様、よろしくお願いいたします！'
        '''
        parsed = me.parse(s)

        ls = (parsed
            .split('\nEOS\n')[0]  # 終端子を除く
            .split('\n')  # 改行で分割（改行区切りで単語が入っている為）
            )

        # 指定の品詞の単語の基本形を抽出してリストへ
        ls = [s.split('\t')[2] # タブで区切った3つ目が基本形
            for s in ls 
            if _judge(s.split('\t')[3])  # タブで区切った4つ目が品詞
            ]
        
        # 1文字の単語は除く
        ls = [s for s in ls if len(s)>1]

        # 重複は除く
        ls = list(set(ls))

        if len(ls)==0:
            return None
        return ls

    cmp = re.compile('^.*形容詞|名詞.*$')
    me = MeCab.Tagger ("-Ochasen")
    return sr.apply(_apply_func_get_word_list)


def get_word_in_name(sr: pd.Series) -> list:
    '''
    debug用
        sr = get_word_list(df_chat[NAME_COLUMN])
    '''
    result_ls = []
    for ls in sr.values:
        if ls is not None:
            result_ls.extend(ls)
    result_ls = list(set(result_ls))        
    return result_ls


def plot_network(sr: pd.Series, ng_list: list, th_lowest_cnt: int, n_word_max: int) -> None:
    '''    
    概要
        JACCARD係数の算出 両方を含む / どちらかを含む
        共起ネットの可視化、出力
        参考) https://qiita.com/y_itoh/items/7aa33ba0b1e30b3ea33d

    parameters
    ----------
    sr: 
        単語リストのシリーズ
    ng_list:
        NG単語（除外対象）のリスト
    th_lowest_cnt:
        最低出現頻度
    n_word_max:
        表示する単語数の上限

    debug用
        sr = df_chat[WORD_LIST_COLUMN]
        th_lowest_cnt = 3
    '''
    noun_list = []
    for word_list in sr:
        if word_list is not None:
            ls = [s for s in word_list if s not in ng_list]
            if len(ls)>1:
                noun_list.append(ls)
    # ex. ['挙手', 'ボタン', '位置']

    # 文単位の名詞ペアリストを生成
    pair_list = [
                list(itertools.combinations(n, 2))
                for n in noun_list if len(noun_list) >=2
                ]
    # ex. [('挙手', 'ボタン'), ('挙手', '位置'), ('ボタン', '位置')]

    # 名詞ペアリストの平坦化
    all_pairs = []
    for u in pair_list:
        all_pairs.extend(u)
    # ex. ('挙手', 'ボタン')
    # ex. ('挙手', '位置')

    # 名詞ペアの頻度をカウント
    cnt_pairs = Counter(all_pairs)
    # ex. ('挙手', 'ボタン'): 3,
    # ex. cnt_pairs[('挙手', 'ボタン')]  # 3

    # 出現頻度にしきい値適用
    cnt_pairs = {k: v for k, v in cnt_pairs.items() if v>=th_lowest_cnt}

    # 出現頻度上位x組に限定
    nmax = n_word_max
    if len(cnt_pairs) < n_word_max:
        nmax = len(cnt_pairs)
    tops = sorted(
    cnt_pairs.items(), 
    key=lambda x: x[1], reverse=True
    )[:nmax]

    # 重み付きデータの生成
    noun_1 = []
    noun_2 = []
    frequency = []
    for n,f in tops:
        noun_1.append(n[0])
        noun_2.append(n[1])
        frequency.append(f)
    df = pd.DataFrame({'word1': noun_1, 'word2': noun_2, '出現頻度': frequency})
    weighted_edges = np.array(df)

    # グラフオブジェクトの生成
    G = nx.Graph(facecolor='red')

    # 重み付きデータの読み込み
    G.add_weighted_edges_from(weighted_edges)

    # ネットワーク図の描画
    for i in range(10):  # 配置いろいろ10枚出す
        plt.close(1)    
        fig = plt.figure(1, figsize=(16, 9), 
            tight_layout=True,)
        ax = fig.add_subplot(111)
        ax.axis('off')

        params = {
            #'node_list': 
            'pos': nx.spring_layout(G, k=0.45),
            'node_shape': "o",
            'node_color': "#E0F7FA",
            'node_size': 500,
            'alpha': 0.9,
            'linewidth': 0,  # symbol border
            'edge_color': "gray", 
            'font_family': "IPAexGothic",
            'font_size': 12,
            'width': 0.5,
            'style': 'dotted',
            'font_color': '#303F9F',
            'ax': ax,
        }
        nx.draw_networkx(G,**params)

        path = f'../data/output/network_{i:02d}.png'
        fig.savefig(path, bbox_inches='tight', pad_inches=0.1, dpi=100)
        print(f'output: {path}')

    return None


if __name__=='__main__':
    # 引数の処理
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='zoom chatのテキストファイルのパス')
    parser.add_argument('--n_word_max', help='表示単語数上限')

    args = parser.parse_args()
    path = args.path
    n_word_max = int(args.n_word_max)

    main(path, n_word_max)
