# coding: utf-8
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

def main(
    chat_path: str, ng_list_path:str, 
    n_word_max: int, th_lowest_cnt: int) -> None:
    '''
    paramters
    -------------
    n_word_max: int
        表示単語数上限

    th_lowest_cnt: int
        最低出現頻度

    debug用
        chat_path = '../data/input/meeting_saved_chat.txt'
        ng_list_path = '../data/input/ng_list.txt'
        n_word_max = 80
        th_lowest_cnt = 1
    '''

    df_chat = load_chat(chat_path)
    ng_list = load_ng_list(ng_list_path)

    # 発言内容の単語リストを取得し、その列を追加
    df_chat = preprocess_chat(df_chat)
    df_chat[WORD_LIST_COLUMN] = get_word_list(df_chat[TEXT_COLUMN])

    # 名前から生じる単語リストを取得し、NGワードに追加
    name_word_list  = get_word_in_name(
            get_word_list(df_chat[NAME_COLUMN]))
    ng_list = ng_list + name_word_list
    del name_word_list

    # jaccard係数算出
    df_edges = preprocess_plot(df_chat[WORD_LIST_COLUMN], ng_list, 
        th_lowest_cnt)

    # plot
    for i in range(10):  # 配置いろいろ10枚出す
        fig = plot(df_edges, n_word_max)
        path = f'../data/output/network_{i:02d}.png'
        fig.savefig(path, bbox_inches='tight', pad_inches=0.1, dpi=85)
        print(f'output: {path}')

    return None


def load_chat(path: str) -> pd.DataFrame:
    '''
    '''
    names = [TIME_COLUMN, TEXT_ORG_COLUMN]
    df = pd.read_csv(path, sep='\t', header=None, names=names)
    print(path, df.shape)
    return df
    

def load_ng_list(path: str or None) -> list:
    if path is None:
        print('None ng list')
        return []
    try:
        with open(path, 'r') as f:
            ls = f.readlines()
            ls = [s.replace('\n', '') for s in ls]
            print('load ng list', path)
            print(ls)
            return ls
    except:
        print('warning! ng_listの読み込み失敗', path)
        return []


def preprocess_chat(df: pd.DataFrame) -> pd.DataFrame:
    '''
    '''
    def _apply_func_get_name(x):
        '''
        debug用
            x = df_chat[TEXT_ORG_COLUMN].values[0]
        '''
        try:
            name = str(x).split(':')[0].split(' ')[2]
        except:
            name = ''
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

    # : を含む行だけ残す
    flags = df[TEXT_ORG_COLUMN].str.contains(':')
    if flags.sum()==0:
        print(df.head(3).T)  # データの例示
        message = f'{TEXT_ORG_COLUMN}列に「:」を含むレコードがありません'
        raise Exception(message)
    else:
        df = df.loc[flags, :].copy()

    # 発言者と内容の取り出し
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


def preprocess_plot(sr: pd.Series, ng_list: list, th_lowest_cnt: int) -> pd.DataFrame():
    '''    
    概要
        JACCARD係数の算出 両方を含む / どちらかを含む

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
    print('ng_list:')
    print(ng_list)

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
    nmax = 1000
    if len(cnt_pairs) < nmax:
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
    df = pd.DataFrame({'word1': noun_1, 'word2': noun_2, 'weight': frequency})        
    return df


def plot(df, n_word_max):
    '''
    debug:
        df = df_edges.copy()
    '''

    '''
    if '居心地' in set(list(df['word1'])+list(df['word2'])):
        print('居心地')
        raise
    '''

    # つながりが少ない単語は除く
    tmp = pd.concat([
        df['word1'].value_counts(),
        df['word2'].value_counts()], axis=1)
    words = tmp[tmp.sum(axis=1)>10].index

    flags = (
        (df['word1'].isin(words))
        |(df['word2'].isin(words))
    )
    df = df.loc[flags, :].copy()

    # 上位x個抽出
    df = df.sort_values(by='weight', ascending=False).head(n_word_max)

    # weightをedge強度に使う。指定範囲に収まるよう加工
    edge_vmax = 1
    edge_vmin = 0.02
    edge_vrange = edge_vmax - edge_vmin
    df['weight'] = df['weight'] - df['weight'].min()  # 
    df['weight'] = df['weight'] / df['weight'].max()  # 0-1
    df['weight'] = df['weight'] * edge_vrange + edge_vmin

    weighted_edges = np.array(df)

    plt.close(1)
    fig = plt.figure(1, figsize=(12, 8), 
        tight_layout=True,)
    ax = fig.add_subplot(111)
    ax.axis('off')
    ax.set(facecolor = "orange")

    # グラフオブジェクトの生成
    G = nx.Graph()
    # node追加
    for u, v, d in weighted_edges:
        G.add_edge(u, v, weight=d)
    # 座標決定
    pos=nx.spring_layout(
        G, 
        #k=0.45, 
        #iterations=100,
        )
    # ノード描画
    nx.draw_networkx_nodes(
        G, pos, node_size=800, node_color="#E0F7FA", 
        alpha=0.9, ax=ax, node_shape='o')
    # テキスト描画
    nx.draw_networkx_labels(
        G, pos, font_size=9, font_family='IPAexGothic',
        font_color='#303F9F', ax=ax)
    # edge描画
    for u, v, d in weighted_edges:
        print(u,v,d)
        nx.draw_networkx_edges(
            G, pos, edgelist=[(u, v)],
            width=2, edge_color=[d], 
            ax=ax, 
            edge_cmap=plt.cm.Blues, edge_vmin=0, edge_vmax=edge_vmax)
    return fig


if __name__=='__main__':
    # 引数の処理
    parser = argparse.ArgumentParser()
    parser.add_argument('--chat_path', help='必須')
    parser.add_argument('--ng_list_path', help='', default=None)
    parser.add_argument('--n_word_max', help='', default='65')
    parser.add_argument('--th_lowest_cnt', help='', default='2')
    args = parser.parse_args()
    chat_path = args.chat_path
    ng_list_path = args.ng_list_path
    n_word_max = int(args.n_word_max)
    th_lowest_cnt = int(args.th_lowest_cnt)

    main(chat_path, ng_list_path, n_word_max, th_lowest_cnt)
