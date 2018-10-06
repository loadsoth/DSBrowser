# -*- coding: utf-8 -*-
"""
ダビマス血統サーチ用、データベース作成スクリプト
データベース作成
立ち上げると、血統が追加されているかチェックして、されている分を取り込んでいく

初期データベースファイル作成が必要な場合時のみ、main()内の
#sq_newdata()
の#を外して、データベースの新規作成を実行する
"""
import sys
import pandas as pd
import csv
import urllib.request
from bs4 import BeautifulSoup
import re
import time
import sqlite3
import copy

#ここで更新するデータベースを指定することでもデータベースファイルの切り替えは可能
DB_NAME = 'derbymas.db'
#DB_NAME = 'sub.db'


INB_NAME = 'ds_inb.csv'

def derby_scraper( flg ):
    
    if flg == 'm':
        print('種牡馬チェック')
        readlist = get_url('http://dabimas.jp/kouryaku/stallions')#urlを変えれば牝馬も読める
    elif flg == 'f':
        print('繁殖牝馬チェック')
        readlist = get_url('http://dabimas.jp/kouryaku/broodmares')#牝馬
        
    newlist = check_url( readlist , flg )#データベースをチェックして、まだデータにない馬をリストに取得

    
    for l in newlist:
        if flg == 'm':
            add_data(l,'m')
        elif flg == 'f':
            add_data(l,'f')

    
    #インブリード効果に新しいものがあるかをチェックする機能を追加
    inblist = read_inb_data()#元データを読み込む
    inblist = check_horse(newlist,inblist)#更新したデータを取得
    write_inb_data(inblist)#データを書き込み



def add_data(u , flg):
    #馬のデータを取り込みDBに登録 flgは種牡馬 'm' か牝馬 'f' か
    #登録済みのcsvファイルに保存する# u はこの形で来る '/kouryaku/broodmares/6428983815.html'
    rare = ['','//cf.dabimas.jp/kouryaku/images/stallion/ss_stallion_rare_01.png',
            '//cf.dabimas.jp/kouryaku/images/stallion/ss_stallion_rare_02.png',
            '//cf.dabimas.jp/kouryaku/images/stallion/ss_stallion_rare_03.png',
            '//cf.dabimas.jp/kouryaku/images/stallion/ss_stallion_rare_04.png',
            '//cf.dabimas.jp/kouryaku/images/stallion/ss_stallion_rare_05.png']
    frare = ['','//cf.dabimas.jp/kouryaku/images/stallion/list_icn_cat_sale_08.png',#無印
             '//cf.dabimas.jp/kouryaku/images/stallion/list_icn_cat_sale_07.png',#可
             '//cf.dabimas.jp/kouryaku/images/stallion/list_icn_cat_sale_06.png',#良
             '//cf.dabimas.jp/kouryaku/images/stallion/list_icn_cat_sale_05.png',#優
             '//cf.dabimas.jp/kouryaku/images/stallion/list_icn_cat_sale_09.png']#名牝
    
    zure = 0
    data = []
    tmpblood = []
    tmpblood2 = []
    output_data = []
    co_flg = 0#コラボ馬の判定用

    readurl = 'http://dabimas.jp' + u
    print(readurl)
    page = pd.read_html( readurl , flavor = 'html5lib')
    #print(len(page))#牝馬は5 牡馬は6
    if flg == 'm':
        zure = 1#テーブル数の調整
    #名前
    page[0].to_csv( 'test.csv' , encoding = 'utf-8' )
    f_name = 'test.csv'
    f = csv.reader( open( f_name , encoding='utf-8' ) )
    for row in f:
        data.append(row)
    if flg == 'm':
        output_data.append( data[2][2] )#馬名
    elif flg == 'f':
        output_data.append( data[1][2] )#馬名

    #レアリティをチェックするのはbs4を使わないと取れないので(牝馬のレアリティも)
    #20180922大幅修正
    time.sleep(1.5)
    url = urllib.request.urlopen(readurl)
    Soup = BeautifulSoup(url,'lxml')
    if flg == 'm':#牡馬のレア度チェック
        hlist = Soup.find_all('img',alt='レアリティ')
        for h in hlist:
            tmp = h.get('src')#tmpでソースの文字列を取得
            for j,k in enumerate( rare ):#レア度を探る
                if tmp == k:#一致すれば、その番号がレア度
                    output_data.append( str(j) )#レア度はstrで
                    co_flg = 1
                    break
        if co_flg == 0:#コラボ馬（レア判別用の枠のimgがない場合の処理
            st = Soup.find_all(attrs = {"src" : "//cf.dabimas.jp/kouryaku/images/stallion/stallion_list_star.png"})
            output_data.append( len(st) )#レア度を表す星の数を数える（全部これで行ける気もするが、この処理は後付けなのでまあこのままで
        co_flg = 0
                    
    elif flg == 'f':#牝馬のレア度チェック
        hlist = Soup.find_all('img')#レアリティを表示するimgを探す
        for h in hlist:
            tmp = h.get('src')
            if 'cat_sale' in tmp:#'sale'という文字列が必ず存在し存在するファイル名はその画像だけなのでチェック
                for j,k in enumerate( frare ):#牝馬のレア度を探る
                    if tmp == k:#一致すれば、その番号がレア度
                        output_data.append( str(j) )
                        break



    del data[:]
    page[2 + zure].to_csv( 'test.csv' , encoding = 'utf-8' )
    f_name = 'test.csv'
    f = csv.reader( open( f_name , encoding='utf-8' ) )
    for row in f:
        data.append(row)
    tmpblood = get_blood(data)#血統データから必要な部分を抜き出して返してくる処理
    for i in tmpblood:
        output_data.append(i)

    del data[:]
    page[3 + zure].to_csv( 'test.csv' , encoding = 'utf-8' )
    f_name = 'test.csv'
    f = csv.reader( open( f_name , encoding='utf-8' ) )
    for row in f:
        data.append(row)
    tmpblood2 = get_blood(data)#血統データから必要な部分を抜き出して返してくる処理
    for i in tmpblood2:
        output_data.append(i)

    write_data( u , output_data , flg )#データベースに読み込んだデータを登録


def check_url(inlist , flg ):
    # u はこの形で来る '/kouryaku/broodmares/6428983815.html'
    #既にDB登録済みの馬のリストと照合して、未登録のurlのリストを返す
    #flg -> f or m
    retlist = []

    conn = sqlite3.connect( DB_NAME )#ファイル名を入力
    curs = conn.cursor()
    

    #未登録の馬かどうかデータベースのテーブル参照
    for i in range(len(inlist)):
        if flg == 'm':
            sql = "select * from chktable_s where chk in (:name)"#牡馬のテーブル更新
        elif flg == 'f':
            sql = "select * from chktable_b where chk in (:name)"#牝馬のテーブル更新

        curs.execute(sql,{"name":inlist[i]})
        r = curs.fetchall()
        if len(r) != 0:
            print('already exist')
        else:
            print('add list')
            retlist.append(inlist[i])

    conn.commit()
    conn.close()
    return retlist


def get_blood(data):#血統データから必要な部分を抜き出して返す処理
    retlist = []
    retlist.append(data[1][2])
    retlist.append(data[2][2])
    retlist.append(data[3][2])
    retlist.append(data[4][2])
    retlist.append(data[5][3])
    retlist.append(data[6][3])
    retlist.append(data[7][2])
    retlist.append(data[8][3])
    retlist.append(data[9][3])
    retlist.append(data[10][2])
    retlist.append(data[11][2])
    retlist.append(data[12][3])
    retlist.append(data[13][3])
    retlist.append(data[14][2])
    retlist.append(data[15][3])
    return retlist


def get_url(u):
    #馬一覧のトップページから馬のURLを取得する
    retlist = []
    tmp = ''
    #馬のデータの読み込み先は、10桁の数字を含むurlなのでそれを抽出する処理
    sh = re.compile('[0-9]{10}\.html')
    url = urllib.request.urlopen(u)
    Soup = BeautifulSoup(url,'lxml')
    list = Soup.find_all('a')
    for i in list:
        tmp = i.get('href')
        if re.search(sh, tmp):
            retlist.append(tmp)
    return retlist


def sq_newdata():#データベース新規作成の時だけ使用
    #必要なテーブルはデータベース登録済みチェック用テーブル、メインデータ、自家生産馬、が種牡馬と繁殖牝馬分必要
    conn = sqlite3.connect( DB_NAME )#ファイル名を入力
    curs = conn.cursor()

    sql = """CREATE TABLE stallionsdata( horsename , rarepoint ,
                                blood00 , blood01 , blood02 , blood03 , blood04 ,
                                blood05 , blood06 , blood07 , blood08 , blood09 ,
                                blood10 , blood11 , blood12 , blood13 , blood14 ,
                                pedigree00 , pedigree01 , pedigree02 , pedigree03 , pedigree04 ,
                                pedigree05 , pedigree06 , pedigree07 , pedigree08 , pedigree09 ,
                                pedigree10 , pedigree11 , pedigree12 , pedigree13 , pedigree14 
                               )
    """
    curs.execute(sql)
    sql = """CREATE TABLE broodmaresdata( horsename , rarepoint ,
                                blood00 , blood01 , blood02 , blood03 , blood04 ,
                                blood05 , blood06 , blood07 , blood08 , blood09 ,
                                blood10 , blood11 , blood12 , blood13 , blood14 ,
                                pedigree00 , pedigree01 , pedigree02 , pedigree03 , pedigree04 ,
                                pedigree05 , pedigree06 , pedigree07 , pedigree08 , pedigree09 ,
                                pedigree10 , pedigree11 , pedigree12 , pedigree13 , pedigree14 
                               )
    """
    curs.execute(sql)
    sql = """CREATE TABLE origin_sdata( horsename , rarepoint ,
                                blood00 , blood01 , blood02 , blood03 , blood04 ,
                                blood05 , blood06 , blood07 , blood08 , blood09 ,
                                blood10 , blood11 , blood12 , blood13 , blood14 ,
                                pedigree00 , pedigree01 , pedigree02 , pedigree03 , pedigree04 ,
                                pedigree05 , pedigree06 , pedigree07 , pedigree08 , pedigree09 ,
                                pedigree10 , pedigree11 , pedigree12 , pedigree13 , pedigree14 
                               )
    """
    curs.execute(sql)
    sql = """CREATE TABLE origin_bdata( horsename , rarepoint ,
                                blood00 , blood01 , blood02 , blood03 , blood04 ,
                                blood05 , blood06 , blood07 , blood08 , blood09 ,
                                blood10 , blood11 , blood12 , blood13 , blood14 ,
                                pedigree00 , pedigree01 , pedigree02 , pedigree03 , pedigree04 ,
                                pedigree05 , pedigree06 , pedigree07 , pedigree08 , pedigree09 ,
                                pedigree10 , pedigree11 , pedigree12 , pedigree13 , pedigree14 
                               )
    """
    curs.execute(sql)    
    sql = "create table chktable_s( url )"
    curs.execute(sql)
    sql = "create table chktable_b( url )"
    curs.execute(sql)
    conn.commit()
    conn.close()


def write_data( url , dat , flg):#url 重複チェックファイル書込 row 書き込むデータ   flg 牡馬牝馬
    conn = sqlite3.connect( DB_NAME )#ファイル名を入力
    curs = conn.cursor()

    u = []
    u.append(url)
    u.append('')#１カラムだとエラーが出るので、ダミーをとりあえず使う
    if flg == 'm':#牡馬
        sql = """INSERT INTO stallionsdata VALUES ( ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? )"""
        curs.execute(sql,dat)
        sql = """insert into chktable_s VALUES ( ? , ? ) """
        curs.execute(sql,u)
    elif flg == 'f':
        sql = """INSERT INTO broodmaresdata VALUES ( ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? )"""
        curs.execute(sql,dat)
        sql = "INSERT INTO chktable_b VALUES ( ? , ?)"
        curs.execute(sql,u)
    conn.commit()
    conn.close()


#インブリード効果の辞書更新のためのスクリプト作成中
def inbreed_search():
    #urllist = get_url('http://dabimas.jp/kouryaku/stallions')#まずは種牡馬の血統記載先のurl
    urllist = get_url('http://dabimas.jp/kouryaku/broodmares')#
    #inblist = check_horse(urllist)
    #print(urllist)
    inblist = read_inb_data()#元データを読み込む
    inblist = check_horse(urllist[200:],inblist)#更新したデータを取得
    write_inb_data(inblist)#データを書き込み


#csvファイルからインブリードの名前：効果のペアのリストを読込
def read_inb_data():
    data = []
    f = csv.reader( open( INB_NAME , encoding='utf-8' ) )
    for row in f:
        data.append(row)
    return data


#インブリードの名前：効果のペアのリストをcsvファイルに保存
def write_inb_data(data):
    with open( INB_NAME , 'w', newline='' , encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(data)


#インブリード効果のある馬に新しい馬が登場していないかチェック
def check_horse(lst , data):
    for u in lst:
        name = ''
        inb = ''
        tmp_data = ['','']
        time.sleep(1.5)
        url = urllib.request.urlopen( 'http://dabimas.jp' + u )
        print(u)
        soup = BeautifulSoup(url,'lxml')
        ls = soup.find_all('table',class_ = 'pedigree')#まずテーブルを抜き出す
        horse_tr = ls[0].find_all('tr')#検索対象の馬のテーブルのtr要素を抜き出す
        for h in horse_tr:
            #テーブル内の馬で、IMGを持つ馬がインブリード要素を持つ馬
            chk_img = h.find_all('img')
            if len(chk_img) != 0:#空ならNone、いればimgタグのリストを取れる
                name = h.text
                name = name.replace('父','')
                name = name.replace('母','')
                
                for img in chk_img:
                    if img.get('src') == '//cf.dabimas.jp/kouryaku/images/stallion/factor_01.png':
                        inb += ' 短距離'
                    elif img.get('src') == '//cf.dabimas.jp/kouryaku/images/stallion/factor_02.png':
                        inb += ' 速力'
                    elif img.get('src') == '//cf.dabimas.jp/kouryaku/images/stallion/factor_03.png':
                        inb += ' 底力'
                    elif img.get('src') == '//cf.dabimas.jp/kouryaku/images/stallion/factor_04.png':
                        inb += ' 長距離'
                    elif img.get('src') == '//cf.dabimas.jp/kouryaku/images/stallion/factor_05.png':
                        inb += ' ダート'
                    elif img.get('src') == '//cf.dabimas.jp/kouryaku/images/stallion/factor_06.png':
                        inb += ' 丈夫'
                    elif img.get('src') == '//cf.dabimas.jp/kouryaku/images/stallion/factor_07.png':
                        inb += ' 早熟'
                    elif img.get('src') == '//cf.dabimas.jp/kouryaku/images/stallion/factor_08.png':
                        inb += ' 晩成'
                    elif img.get('src') == '//cf.dabimas.jp/kouryaku/images/stallion/factor_09.png':
                        inb += ' 堅実'
                    elif img.get('src') == '//cf.dabimas.jp/kouryaku/images/stallion/factor_10.png':
                        inb += ' 気性難'
                #print(name + inb)#あとで馬名から父と母の文字を消すprint(inb)
                tmp_data[0] = name
                tmp_data[1] = inb
                if tmp_data not in data:
                    print('add {} data'.format(tmp_data))
                    data.append( copy.copy(tmp_data) )
                inb = ''
    return data

        

if __name__ == '__main__':
    if len(sys.argv) > 1:
        DB_FILE = sys.argv[1]#スクリプト起動時にdb読み込みファイル名を指定可能に
    #新規データ作成時は下のメソッドをコメントアウト外して実行
    #sq_newdata()#新規データベースファイル作成メソッド

    derby_scraper('m')#f or m 性別
    derby_scraper('f')


