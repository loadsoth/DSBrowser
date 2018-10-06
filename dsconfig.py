# -*- coding: utf-8 -*-
#import sqlite3

stallions =[]#種牡馬のデータ
broodmares =[]#繁殖牝馬のデータ

st_origin = []#自家製馬
br_origin = []#自家製馬
st_tmp = []#保存しない自家製馬のデータ
br_tmp = []#保存しない自家製馬のデータ
abi = []#非凡のデータ



S_LIMIT = 3#2代検索時の牡馬のレア度のデフォルト下限
B_LIMIT = 3#2代検索時の牝馬のレア度のデフォルト下限
describe = 0



#デフォルトのデータベースファイル名
DB_FILE = 'derbymas.db'

tmpcheck = 0#自家製馬をデータベースに保存する場合は0、保存しない場合は1を立てる
inbreed = {}#inbreed効果辞書


#系統の短縮形辞書
hblood = {'Eclipse':'Ec','Fairway':'Fa','Hampton':'Hmp','Herod':'Her','Himyar':'Him',
          'Native Dancer':'ND','Nasrullah':'Nas','Nearctic':'Nea','Matchem':'Mach',
          'St.Simon':'Sts','Swynford':'Swn','Phalaris':'Pha',
          'Royal Charger':'RC','Teddy':'Ted','Tom Fool':'Tom',}


#インブリード表示用テキスト、クラス対応バージョン(空白を抜いた)
fmnew = ('父     ','父父    ','父父父  ','父父父父','父父母父','父母父  ','父母父父','父母母父',
      '母父    ','母父父  ','母父父父','母父母父','母母父  ','母母父父','母母母父')


#インブリードや配合をチェックする汎用メソッド
bloodlist = ('Ec','Fa','Hmp','Her','Him','ND','Nas','Nea','Mach',
                 'Sts','Swn','Pha','RC','Ted','Tom')#系統の短縮名


#面白判定になりうるかどうかをチェック
#引数は短縮された系統名のリスト。それが7/8種類かどうかを判定しT/Fを返す
def search_funny( eight_list ):
    ret = False
    count = 0

    for i in bloodlist:
        for j in eight_list:
            if i == j:
                count += 1
                break

    if count >= 7:
        ret = True
    return ret


#見事な配合が成立するか判定するメソッド 見事配合ならTrueを返す
#引数は系統の名前4つが入ったリストが2頭分
def search_great( flist , mlist ):
    ret = False
    fflg = [0,0,0,0]
    mflg = [0,0,0,0]

    for i in range(0,4):
        for j in range(0,4):
            if flist[i] == mlist[j]:
                fflg[i] = 1
                mflg[j] = 1

    if fflg[0] and fflg[1] and fflg[2] and fflg[3]:
        if mflg[0] and mflg[1] and mflg[2] and mflg[3]:
            ret = True

    return ret


#よくできた配合が成立するか判定するメソッド
#引数 flistは牝馬の面白配合 mlist は牡馬の見事用配合 のそれぞれの短縮系統名
#4本のうち3本が合致すればよくできた配合成立
def search_good( flist , mlist ):
    ret = False
    fflg = [0,0,0,0]
    mflg = [0,0,0,0]

    for i in range(0,4):
        for j in range(0,4):
            if flist[i] == mlist[j]:
                fflg[i] = 1
                mflg[j] = 1

    if ( fflg[0] + fflg[1] + fflg[2] + fflg[3] ) >= 3:
        if ( mflg[0] + mflg[1] + mflg[2] + mflg[3] ) >= 3:
            ret = True
    return ret


#引数の血統名に有効なインブリード効果があれば、その効果を返す
def get_inbreed( bl_name ):
    ret = ''
    for i in inbreed:#辞書テーブルをチェック
        if bl_name == i:
            ret = inbreed[i]
    return ret




