# -*- coding: utf-8 -*-
"""
ダビマス　才能一覧を取得する
"""
import urllib.request
from bs4 import BeautifulSoup
import re
import csv

FILENAME = 'ds_abi.csv'#保存するファイル名

#ダビマスの、非凡や才能の能力一覧をゲットしてcsvに保存
class ds_abilities():
    def __init__(self,master = None):
        self.read_data()


    def read_data(self):
        url = 'https://dabimas.jp/kouryaku/abilities'#読み込み元のURL
        res = urllib.request.urlopen(url)
        soup = BeautifulSoup(res , 'lxml')
        output = []#出力用リスト


        ls = soup.find_all('div',class_ = 'title_panel ability_index')#データを才能単位で取得し、テキストを処理していく
        tmp = []#保存項目 [0]名前 [1]説明[2]入手経路[3]発揮効果[4]発揮条件[5]発揮対象[6]発揮確率
        txt = ''
        for l in ls:
            tmp = self.get_txt( l.text )#soupのデータのリストには、個々の才能データが入る。そのテキストから情報を抽出する
            output.append(tmp)

        self.save_csv(output)#保存

    #csvに保存
    def save_csv(self , listdata ):
        with open(FILENAME , 'w', newline='' , encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(listdata)



    #引数の文字列から、保存用のテキストをリスト形式で返す
    #保存項目 [0]名前 [1]説明[2]入手経路[3]発揮効果[4]発揮条件[5]発揮対象[6]発揮確率
    # データの例 'しょうせい将星説明愛や情けを捨て去り聖帝として競馬界に君臨する入手経路アイナドイラヌ20XX
    # 概要発揮効果・効果1（条件を満たすと発揮）\n\u3000最後の直線で脚が速くなる\n・効果2（条件を満たすと発揮）
    # \n\u3000最後の直線で、対象を疲れやすくする発揮条件・短距離以上のレース\n・ダートレース\n・騎乗指示：先行
    #\n・人気が高い発揮対象効果1\n\u3000自分\n・効果2\n騎乗指示：逃げ\u3000相手競走馬2頭発揮確率・100%'
    def get_txt( self , txt):
        ret = ['','','','','','','']

        tap0 = re.search(r'説明',txt)#文字列を分割する位置を探る
        ret[0] = txt[ : tap0.span(0)[0] ]#名前
        tap1 = re.search(r'入手経路',txt)#文字列を分割する位置を探る
        ret[1] = txt[ tap0.span(0)[1] : tap1.span(0)[0] ]#説明
        tap2 = re.search(r'概要発揮効果',txt)
        ret[2] = txt[ tap1.span(0)[1] : tap2.span(0)[0] ]#入手経路
        tap3 = re.search(r'発揮条件',txt)
        ret[3] = txt[ tap2.span(0)[1] : tap3.span(0)[0] ]#発揮効果
        tap4 = re.search(r'発揮対象',txt)
        ret[4] = txt[ tap3.span(0)[1] : tap4.span(0)[0] ]#発揮条件
        tap5 = re.search(r'発揮確率',txt)
        ret[5] = txt[ tap4.span(0)[1] : tap5.span(0)[0] ]#発揮対象
        ret[6] = txt[ tap5.span(0)[1]: ]#発揮確率

        return ret



if __name__ == '__main__':
    ds = ds_abilities()
