# -*- coding: utf-8 -*-
import sqlite3
#from tkinter import *
import tkinter as tk
import tkinter.font as Ft
#from tkinter.scrolledtext import *
from tkinter.scrolledtext import ScrolledText
import tkinter.messagebox as Mb
import copy
import sys
import csv
import re

import dsconfig as ds
ABI_FILE = 'ds_abi.csv'#非凡、才能の説明ファイル
INB_FILE = 'ds_inb.csv'#インブリード持ち馬名、効果のファイル



class topframe():#一番最初に読み込まれるフレーム。ここから子フレームを呼び出す
    def __init__( self , master = None ):
        #super(topframe,self).__init__()
        self.mainframe = tk.Tk()
        self.setVar()
        self.data_init()
        self.mframe = mainbrowser( self.mainframe )
        self.oframe = originbrowser( self.mainframe )
        self.abcdframe = abcdbrowser( self.mainframe )

        
        self.setWidgets()
        self.setMenu( self.mainframe )
        
        self.show_main_browser()


    def setVar(self):
        self.rarelimit = tk.IntVar()
        self.rarelimit.set(3)#検索対称のレア度下限設定のデフォルト
        self.rarelimitB = tk.IntVar()


        self.rarelimitB.set(3)#検索対称のレア度下限設定のデフォルト
        self.tmpthrough = tk.BooleanVar()#自家製馬をデータベースに保存する場合は0、保存しない場合は1を立てる
        self.tmpthrough.set(False)
        


    def setWidgets ( self ):
        self.font_button = Ft.Font(size = 12 , family = 'Arial' , weight = 'bold' )
        
        self.f0 = tk.Frame( self.mainframe , relief=tk.RIDGE, bd=3 )#親フレーム
        #機能切り替えボタン1
        self.btload01 = tk.Button(self.f0, text='A-(BC)サーチ', bg='deep sky blue', font = self.font_button ,
                             bd=3 , padx =3 , command = self.show_main_browser )
        self.btload01.grid(row = 0 , column = 0)
        #機能切り替えボタン2
        self.btload02 = tk.Button(self.f0, text='自家製メンテ', bg='red', font = self.font_button ,
                             bd=3 , padx =3 , command = self.show_origin_browser )
        self.btload02.grid(row = 0 , column = 2)
        #機能切り替えボタン3
        self.btload03 = tk.Button(self.f0, text='A-(B-CD)サーチ', bg='azure2', font = self.font_button ,
                             bd=3 , padx =3 , command = self.show_abcd_browser )
        self.btload03.grid(row = 0 , column = 3)
        #機能切り替えボタン4(休止中)
        self.btload04 = tk.Button(self.f0, text='血統検索', bg='azure3', font = self.font_button ,
                             bd=3 , padx =3 , command = self.pop_search_browser )
        #self.btload04.grid(row = 0 , column = 4)
        self.f0.grid(row = 0 , column = 0)


    def setMenu(self , frame ):
        self.menubar = tk.Menu ( frame )
        frame.configure( menu = self.menubar )
        self.limit = tk.Menu( self.menubar , tearoff = False  )
        self.limit.add_radiobutton(label = '牡馬2代検索レア度下限 5' , variable = self.rarelimit ,
                                    value = 5 , command = self.switchlimitS )
        self.limit.add_radiobutton(label = '牡馬2代検索レア度下限 4' , variable = self.rarelimit ,
                                    value = 4 , command = self.switchlimitS )
        self.limit.add_radiobutton(label = '牡馬2代検索レア度下限 3' , variable = self.rarelimit ,
                                    value = 3 , command = self.switchlimitS )
        self.limit.add_radiobutton(label = '牡馬2代検索レア度下限 2' , variable = self.rarelimit ,
                                    value = 2 , command = self.switchlimitS )
        self.limit.add_radiobutton(label = '牡馬2代検索レア度下限 1' , variable = self.rarelimit ,
                                    value = 1 , command = self.switchlimitS )
        self.limit.add_separator()

        self.limit.add_radiobutton(label = '牝馬2代検索レア度下限 5' , variable = self.rarelimitB ,
                                    value = 5 , command = self.switchlimitB )
        self.limit.add_radiobutton(label = '牝馬2代検索レア度下限 4' , variable = self.rarelimitB ,
                                    value = 4 , command = self.switchlimitB )
        self.limit.add_radiobutton(label = '牝馬2代検索レア度下限 3' , variable = self.rarelimitB ,
                                    value = 3 , command = self.switchlimitB )
        self.limit.add_radiobutton(label = '牝馬2代検索レア度下限 2' , variable = self.rarelimitB ,
                                    value = 2 , command = self.switchlimitB )
        self.limit.add_radiobutton(label = '牝馬2代検索レア度下限 1' , variable = self.rarelimitB ,
                                    value = 1 , command = self.switchlimitB )
        self.limit.add_separator()
        self.limit.add_checkbutton ( label = '自家製馬をデータベースに登録しない' , variable = self.tmpthrough ,
                                   onvalue = True , offvalue = False , command =self.set_through )
        self.limit.add_separator()
        self.limit.add_command( label = 'リストデータ更新' , command = self.data_reset )
        self.limit.add_separator()
        #追加
        self.limit.add_separator()
        self.limit.add_command( label = 'テンポラリ馬を削除(仮設' , command = self.data_delete_reset )
        self.limit.add_separator()

        self.menubar.add_cascade(label = '  LIMIT  ' , menu = self.limit )




    def switchlimitS(self):
        ds.S_LIMIT = self.rarelimit.get()


    def switchlimitB(self):
        ds.B_LIMIT = self.rarelimitB.get()        


    def set_through(self):
        ds.tmpcheck = self.tmpthrough.get()#True(1)が立っていたらなら自家製馬を保存しない


    #各フレームの馬リストの再読み込み
    def data_reset(self):
        #データベース初期化
        self.data_init()

        self.mframe.set_list_s()
        self.mframe.set_list_b()
        self.oframe.set_list_s()
        self.oframe.set_list_b()
        self.abcdframe.set_list_first()
        #ここにテンポラリ馬の事をやらないと？



    def data_delete_reset(self):
        #データベースを、テンポラリに一時保存しているデータを削除してデータベースを初期化呼び出し
        print('test')
        del ds.st_tmp[:]
        del ds.br_tmp[:]
        self.data_reset()



    def data_init(self):#データ読み込み処理など
        #ds.db_open()
        del ds.stallions[:]
        del ds.broodmares[:]
        del ds.st_origin[:]
        del ds.br_origin[:]
        
        self.readdata_from_sql()#データベースから馬データを読み込んでくる
        
        #2018/09 非凡表示のデータ読み込みを追加
        self.data_abi_set()
        #2018/09 インブリード効果をファイルから読み込むように変更
        self.data_inbreed_set()



    def readdata_from_sql(self):
        del ds.stallions[:]
        del ds.broodmares[:]

        conn = sqlite3.connect(ds.DB_FILE)
        curs = conn.cursor()
        sql = "select * from stallionsdata order by rarepoint desc,horsename asc"
        curs.execute( sql )
        stallions = curs.fetchall()#種牡馬データ
        sql = "select * from broodmaresdata order by rarepoint desc,horsename asc"
        curs.execute( sql )
        broodmares = curs.fetchall()#繁殖牝馬データ
        sql = "select * from origin_sdata"
        curs.execute( sql )
        st_origin = curs.fetchall()#種牡馬データ
        sql = "select * from origin_bdata"
        curs.execute( sql )
        br_origin = curs.fetchall()#繁殖牝馬データ
        conn.commit()
        conn.close()  
        
        #テンポラリ馬をリストの先頭に追加
        for s in ds.st_tmp:
            ds.stallions.append( s )#テンポラリの馬をリストに追加
        for b in ds.br_tmp:
            ds.broodmares.append( b )#テンポラリの馬をリストに追加
        #データベースから読み込んだデータをリストに追加    
        for s in st_origin:
            ds.stallions.append( horse(s) )#自家製馬データをインスタンスしてクラスにセット
        for b in br_origin:
            ds.broodmares.append( horse(b) )#自家製馬データをインスタンスしてクラスにセット
        for s in stallions:
            ds.stallions.append( horse(s) )#馬データをインスタンスしてクラスにセット
        for b in broodmares:
            ds.broodmares.append( horse(b) )#馬データをインスタンスしてクラスにセット



    #非凡データを読み込む
    def data_abi_set(self):
        with open(ABI_FILE, newline='' , encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                ds.abi.append(row)


    #インブリード効果の辞書を作成する(ds.inbreedが辞書ファイル名として定義してある)
    def data_inbreed_set(self):
        dicdata = []
        #ファイルを読み込んで、リストに保存
        with open(INB_FILE, newline='' , encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                dicdata.append(row)
        #辞書作成
        for d in dicdata:
            ds.inbreed[ d[0] ] = d[1]


    #表示するフレームの切り替え
    def show_main_browser( self ):
        self.mframe.f1.grid(row = 1,column = 0)
        #self.fframe.f1.grid_remove()


    #表示するフレームの切り替え
    def show_origin_browser( self ):
        self.oframe.f1.grid(row = 1,column = 1)
        self.abcdframe.f1.grid_remove()
        #self.liframe.f1.grid_remove()


    #表示するフレームの切り替え
    def show_abcd_browser( self ):
        self.abcdframe.f1.grid(row = 1,column = 1)
        self.oframe.f1.grid_remove()
        #self.liframe.f1.grid_remove()


    #検索フレーム休止中
    def pop_search_browser( self ):
        #tk.Toplevel(class_ = thirdframe() )
        print('pass')



#牡馬からの検索情報を調べるフレーム
class mainbrowser:
    def __init__( self , frame ):
        self.setVar()
        self.setWidgets( frame )
        self.set_list_s()#種牡馬の一覧をリストにセット
        self.set_list_b()#繁殖牝馬の一覧をリストにセット

    #変数初期化
    def setVar ( self ):
        #stlist = []
        self.newname = tk.StringVar()#ダミー
        self.describe = tk.BooleanVar()
        self.describe.set(False)
        #追加(面白配合時のインブリードや系統の確認を行うかどうかのフラグ)
        self.o_describe = tk.BooleanVar()
        self.o_describe.set(False)
        self.a_describe = tk.BooleanVar()
        self.a_describe.set(False)


    #表示ウィジェット初期化 
    def setWidgets( self , frame ):
        self.font_button = Ft.Font(size = 10 , family = 'Arial' , weight = 'bold' )
        self.font_button2 = Ft.Font(size = 9 , family = 'Arial' , weight = 'bold' )

        self.f1 = tk.Frame( frame , relief=tk.RIDGE, bd=2 )#フレーム
        #種牡馬表示リスト
        self.slist = tk.Listbox( self.f1 , height = '16' , width = '70' , selectmode = 'SINGLE' )
        self.sbar = tk.Scrollbar(self.f1, orient = 'v', command = self.slist.yview )
        self.slist.configure(yscrollcommand = self.sbar.set)

        #牝馬表示リスト
        self.blist = tk.Listbox( self.f1 , height = '16' , width = '70' , selectmode = 'SINGLE' )
        self.bbar = tk.Scrollbar(self.f1, orient = 'v', command = self.blist.yview )
        self.blist.configure(yscrollcommand = self.bbar.set)

        #検索ボタン(牡馬
        self.btstallion = tk.Button(self.f1, text='配合情報(牡', bg='light cyan',font = self.font_button ,
                             bd=2 , padx =5 , command = self.call_stallion_show(0))
        #検索ボタン(牝馬
        self.btbroodmare = tk.Button(self.f1, text='配合情報(牝', bg='light cyan',font = self.font_button ,
                             bd=2 , padx =5 , command = self.call_broodmare_show(0))
        #検索表示の設定
        self.describe_check = tk.Checkbutton(self.f1 , text = 'インブリード詳細表示(1代完璧or見事)', variable = self.describe,
                                          onvalue = True , offvalue = False )
        self.describe2_check = tk.Checkbutton(self.f1 , text = '面白種牡馬詳細表示(新規種牡馬作成向け情報)', variable = self.o_describe,
                                          onvalue = True , offvalue = False )
        self.describe3_check = tk.Checkbutton(self.f1 , text = '非凡所持馬詳細表示', variable = self.a_describe,
                                          onvalue = True , offvalue = False )

        #検索ボタン(子) 
        self.btchilds = tk.Button(self.f1, text='子供の情報(牡', bg='spring green',font = self.font_button2 ,
                             bd=2 , padx =5 , command = self.call_stallion_show(1) )
        self.btchildb = tk.Button(self.f1, text='子供の情報(牝', bg='linen',font = self.font_button2 ,
                             bd=2 , padx =5 , command = self.call_broodmare_show(1) )

        self.btstallion.grid(row = 3 , column = 0)
        self.btbroodmare.grid(row = 7 , column = 0)
        self.btchilds.grid( row = 6 , column = 1)
        self.btchildb.grid( row = 7 , column = 1)
        self.describe_check.grid(row = 0 , column = 1)
        self.describe2_check.grid(row = 1 , column = 1)
        self.describe3_check.grid(row = 2 , column = 1)
        
        self.slist.grid( row = 4 , column = 0 , columnspan = 3, sticky = 'ns')
        self.sbar.grid( row = 4 , column = 2 , sticky = 'ns' + 'e')
        self.inbreedwindow = ScrolledText(self.f1 , height = '16' , width = '60' ,
                                      padx = '3' , pady = '3' , relief = 'groove')
        self.inbreedwindow.grid( row = 5 , column = 0 , columnspan = 3)
        
        self.blist.grid( row = 8 , column = 0 , columnspan = 3, sticky = 'ns')
        self.bbar.grid( row = 8 , column = 2 , sticky = 'ns' + 'e')
        #結果表示ウィンドウ
        self.firstwindow = ScrolledText(self.f1 , height = '65' , width = '45' ,
                                      padx = '3' , pady = '3' , relief = 'groove')
        self.firstwindow.grid( row = 4 ,column = 4, rowspan = 5)

        #隠し機能(一部右クリック対応)
        self.btstallion.bind('<Button-3>', self.addBT )#検索ボタンで面白配合の種牡馬一括作成(ｔｍｐとして
        self.btbroodmare.bind('<Button-3>', self.addBT )#検索ボタンで面白配合の種牡馬一括作成(ｔｍｐとして
        self.btchilds.bind('<Button-3>', self.addBT )#検索ボタンｔｍｐとして仔馬の作成
        self.btchildb.bind('<Button-3>', self.addBT )#検索ボタンｔｍｐとして仔馬の作成



    def addBT(self , event):
        snum = 0
        fnum = 0
        couplelist = []

        #推された元のボタンによって処理を変える
        if event.widget == self.btstallion:#牡馬から、面白配合成立の牝馬リストとの種牡馬を一括作成  
            print('tmpに完璧配合可能種牡馬一括作成')
            snum = int( self.slist.get( tk.ACTIVE )[:3] )
            #リスト作成
            omoshiro = ds.stallions[snum].funnysearch('s' , ds.broodmares )
            if len(omoshiro) != 0:
                for o in omoshiro:
                    couplelist.append( ( snum , o) )
                originbrowser.add_tmphorse_from_other( 's' , couplelist )#種牡馬をtmpに作成
                print('...終了')
        elif event.widget == self.btbroodmare:#牝馬から、面白配合成立の種牡馬との種牡馬を一括作成
            print('tmpに完璧配合可能種牡馬一括作成')
            bnum = int( self.blist.get( tk.ACTIVE )[:3] )
            #リスト作成
            omoshiro = ds.broodmares[bnum].funnysearch('b' , ds.stallions )
            if len(omoshiro) != 0:
                for o in omoshiro:
                    couplelist.append( ( o, bnum ) )
                originbrowser.add_tmphorse_from_other( 's' , couplelist )#種牡馬をtmpに作成
                print('...終了')

        elif event.widget == self.btchilds:
            print('tmp作成牡馬')
            snum = int( self.slist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
            fnum = int( self.blist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
            originbrowser.add_tmphorse_from_other( 's' , [(snum , fnum)] )#種牡馬をtmpに作成

        elif event.widget == self.btchildb:
            print('tmp作成牝馬')
            snum = int( self.slist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
            fnum = int( self.blist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
            originbrowser.add_tmphorse_from_other( 'b' , [(snum , fnum)] )#牝馬をtmpに作成


    #リスト選択中の種牡馬、牝馬の組み合わせで出来た馬が繁殖牝馬になった場合の配合情報
    #引数broは繁殖牝馬のデータクラス
    def broodmare_show(self , bro ):
        self.firstwindow.delete( 0.0 , tk.END )
        #新牝馬の処理
        txt = bro.name + '\n\n'#馬名
        self.firstwindow.insert( tk.END , txt )
        
        self.inbreed_st_show( bro )#専用窓に仔のインブリード血統を表示
        
        #great,perfectには、種牡馬の完璧、見事になるリスト番号の配列が返ってくる
        great , perfect = bro.search_cross_to( 'b' , ds.stallions )#種牡馬に対して見事完璧をチェックする

        txt = '\n1代で完璧配合になる種牡馬は...\n'
        self.firstwindow.insert( tk.END , txt )
        if len(perfect) == 0:
            txt = 'なし\n'
            self.firstwindow.insert( tk.END , txt )
        else:
            for i in perfect:
                txt = '    ' + str( ds.stallions[i].rare ) + ' ' + ds.stallions[i].name + '\n'
                self.firstwindow.insert( tk.END , txt , 'blue' )
                self.stallion_inbreed_show( ds.stallions[i] , bro )
                
        txt = '\n\n1代で見事配合になる種牡馬は...\n'
        self.firstwindow.insert( tk.END , txt )
        if len(great) == 0:
            txt = 'なし\n'
            self.firstwindow.insert( tk.END , txt )
        else:
            for i in great:
                txt = '    ' + str (ds.stallions[i].rare) + ' ' + ds.stallions[i].name + '\n'
                self.firstwindow.insert( tk.END , txt , 'blue' )
                self.stallion_inbreed_show( ds.stallions[i] , bro )


        #面白配合になる種牡馬の表示
        txt = '\n\n\n1代で面白い配合になる種牡馬は...\n\n'
        self.firstwindow.insert( tk.END , txt , 'green' )
        omoshiro = []#面白い配合が成立する繁殖牝馬の番号を取得
        omoshiro = bro.funnysearch( 'b' , ds.stallions )
        if len(omoshiro) != 0:
            for i in omoshiro:
                if i not in great and i not in perfect:#見事完璧と重複していれば表示しない
                    txt = '      {} {}\n'.format( ds.stallions[i].name , ds.stallions[i].rare )
                    self.firstwindow.insert( tk.END , txt , 'green' )
                    #追加。詳細表示チェック状態なら、配合で出来た場合の馬のインブリード詳細表示のテキストを返す
                    if self.o_describe.get() == True:
                        txt = self.stallion_omoshirotxt_ret( ds.stallions[i] , bro )
                        self.firstwindow.insert( tk.END , txt)
        else:
            txt = 'なし\n\n\n'
            self.firstwindow.insert( tk.END , txt )






        #牡牝の組み合わせで出来た種牡馬が、見事または完璧な配合の組み合わせがあるのかどうか
        txt = self.search_cross_cross_broodmare( bro )
        self.firstwindow.insert( tk.END , txt )
        

        self.inbreed_st_show( bro )#メイン検索馬インブリード表示専用窓に種牡馬のインブリード血統を表示             
        self.firstwindow.tag_config( 'red' , underline = 1 , background = '#ff9999')
        self.firstwindow.tag_config( 'blue' , underline = 1 , background = '#bbbbff')


    #専用窓に引数の馬クラスのインブリード血統を表示
    def inbreed_st_show(self , horse ):
        self.inbreedwindow.delete( 0.0 , tk.END )
        txt = horse.show_selfdata()
        self.inbreedwindow.insert( tk.END , txt )

        
    #非凡を持っている種牡馬かどうかを名前でチェックし、持っていればテキストを返す
    #引数は馬名、返り値は非凡の説明文非凡がなければ'\n'    
    def stallion_abi(self , name):
        ret = '\n\n'
        for d in ds.abi:
            if name == d[2]:
                ret = '非凡所持\n名前 : {}\n説明 : {}\n発揮効果 : {}\n発揮条件 : {}\n発揮対象 : {}\n発動確率 : {}\n\n'.format(
                        d[0] , d[1] , d[3] , d[4] , d[5] , d[6])
                #print(ret)
                break
        return ret



    #繁殖牝馬からの配合検索情報の表示メソッドをコールする
    #引数 flg...0-> リストから直の繁殖牝馬情報サーチ  flg...1-> リストの種牡馬と牝馬の組み合わせで出来た新繁殖牝馬の情報サーチ
    def call_broodmare_show(self,flg):
        def t():
            if flg == 0:
                current_b = int( self.blist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
                self.broodmare_show( ds.broodmares[current_b] )
            elif flg == 1:
                current_s = int( self.slist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
                current_b = int( self.blist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
                tmphorse = ds.stallions[current_s].make_horse_to_broodmare(ds.broodmares[current_b])
                self.broodmare_show(tmphorse)
        return t



    #種牡馬からの配合検索情報の表示メソッドをコールする
    #引数 flg...0-> リストの種牡馬の情報サーチ  flg...1-> リストの種牡馬と牝馬の組み合わせで出来た新種牡馬の情報サーチ
    def call_stallion_show(self,flg):
        def t():
            if flg == 0:
                current_s = int( self.slist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
                self.stallion_show( ds.stallions[current_s] )
            elif flg == 1:
                current_s = int( self.slist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
                current_b = int( self.blist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
                tmphorse = ds.stallions[current_s].make_horse_to_broodmare(ds.broodmares[current_b])
                self.stallion_show(tmphorse)
        return t





    #リストで選択された馬の基本情報などを表示
    #引数はベースになる種牡馬のデータクラス
    def stallion_show(self , sta ):
        great = []
        perfect = []
        self.firstwindow.delete( 0.0 , tk.END )
        txt = sta.name + '\n\n'#馬名

        #追加...非凡を持っているならば能力を表示する
        if self.a_describe.get():
            txt += self.stallion_abi(sta.name)

        #見事、完璧配合になる繁殖牝馬の番号のリストが返ってくる引数's'は自分の牡牝
        great , perfect = sta.search_cross_to( 's' , ds.broodmares )

        #見事系統と面白系統の8系統のリストを渡す
        if ds.search_funny( sta.omoshiro + sta.migoto ) == True:
            txt += '\n完璧配合が可能な種牡馬です\n\n\n'

        txt += '\n1代で完璧配合になる繁殖牝馬は...\n\n\n'
        self.firstwindow.insert( tk.END , txt )

        if len(perfect) == 0:
            txt = 'なし\n\n'
            self.firstwindow.insert( tk.END , txt )
        else:
            for i in perfect:#完璧対象になる牝馬の配列番号でイテレート
                txt = '    {}: {}\n'.format( ds.broodmares[i].rare ,ds.broodmares[i].name )
                self.firstwindow.insert( tk.END , txt , 'blue' )
                self.stallion_inbreed_show( sta, ds.broodmares[i] )#インブリード情報の表示
                    
                    
        txt = '\n\n\n1代で見事配合になる繁殖牝馬は...\n\n'
        self.firstwindow.insert( tk.END , txt )
        if len(great) == 0:
            txt = 'なし\n\n'
            self.firstwindow.insert( tk.END , txt )
        else:
            for i in great:
                txt = '    ' + ds.broodmares[i].name + ' ' + str ( ds.broodmares[i].rare ) + '\n'
                self.firstwindow.insert( tk.END , txt , 'blue' )
                self.stallion_inbreed_show( sta, ds.broodmares[i] )#インブリード情報の表示


        #よくできた配合になる繁殖牝馬の表示
        txt = '\n\n1代で良くできた配合になる繁殖牝馬は...\n\n'
        yoku = []#よくできた配合が成立する繁殖牝馬の番号を取得
        yoku = sta.goodsearch( 's' , ds.broodmares )
        if len(yoku) != 0:
            for i in yoku:
                if i not in great and i not in perfect:#見事完璧と重複していれば表示しない
                    txt += '      {} {}\n'.format( ds.broodmares[i].name , ds.broodmares[i].rare )
        else:
            txt += 'なし\n\n\n'
        self.firstwindow.insert( tk.END , txt )
        del yoku[:]


        #面白配合になる繁殖牝馬の表示
        txt = '\n\n\n1代で面白い配合になる繁殖牝馬は...\n\n'
        self.firstwindow.insert( tk.END , txt , 'green' )
        omoshiro = []#面白い配合が成立する繁殖牝馬の番号を取得
        omoshiro = sta.funnysearch( 's' , ds.broodmares )
        if len(omoshiro) != 0:
            for i in omoshiro:
                if i not in great and i not in perfect:#見事完璧と重複していれば表示しない
                    txt = '      {} {}\n'.format( ds.broodmares[i].name , ds.broodmares[i].rare )
                    self.firstwindow.insert( tk.END , txt , 'green' )
                    #追加。詳細表示チェック状態なら、配合で出来た場合の馬のインブリード詳細表示のテキストを返す
                    if self.o_describe.get() == True:
                        txt = self.stallion_omoshirotxt_ret( sta , ds.broodmares[i] )
                        self.firstwindow.insert( tk.END , txt)
        else:
            txt = 'なし\n\n\n'
            self.firstwindow.insert( tk.END , txt )
        

        #牡牝の組み合わせで出来た牝馬が、見事または完璧な配合の組み合わせがあるのかどうか
        txt = self.search_cross_cross( sta )
        self.firstwindow.insert( tk.END , txt )
        
        self.inbreed_st_show( sta )#メイン検索馬インブリード表示専用窓に種牡馬のインブリード血統を表示   
        
        self.firstwindow.tag_config( 'blue' , underline = 1 , background = '#bbbbff')
        self.firstwindow.tag_config( 'green' , underline = 1 , background = '#99cc99')




    #機能追加。自家製種牡馬を作ることを想定して、組み合わせて作った時にできる馬の情報をテキストで返す
    #引数は牡馬、牝馬のクラス、返り値は表示用のテキスト
    def stallion_omoshirotxt_ret(self , sta , bro ):
        rettxt = '\n    '
        rettxt += '{} X {} ...\n\n'.format( sta.name , bro.name)
        tmp = sta.make_horse_to_broodmare(bro)
        rettxt += tmp.show_selfdata_light()
        return rettxt + '\n\n'



    def stallion_inbreed_show(self, sta , bro ):#牝馬broの血統と、牡馬staとのインブリード情報をテキスト表示
        #print('sta',sta.blood)
        #print('bro',bro.blood)
        if self.describe.get() == True:#インブリード詳細表示にチェックがある時
            txt = '\n     繁殖牝馬 ' + bro.name + ' の持つ血統\n'
            self.firstwindow.insert( tk.END , txt , 'blue')
            for i , b in enumerate( bro.blood ):
                flg = 0
                tmp = ds.get_inbreed( b )
                txt = '        {:<4} {}        {}\n'.format( ds.fmnew[i] , b , tmp )
                for sb in sta.blood:
                    if b == sb:#インブリードのクロスがあった場合、色を変える
                        flg = 1
                if flg == 1:
                    self.firstwindow.insert( tk.END , txt , 'red' )
                else:
                    self.firstwindow.insert( tk.END , txt )
        else:#詳細表示にチェックがない時、もしインブリードがあればあるかどうかだけ簡易表示する
            txt = sta.check_inbreed_light( bro )
            self.firstwindow.insert( tk.END , txt + '\n\n' )
        
        self.firstwindow.insert( tk.END , '\n\n' )
        self.firstwindow.tag_config( 'red' , underline = 1 , background = '#ff9999')
        self.firstwindow.tag_config( 'blue' , underline = 1 , background = '#bbbbff')




    #引数sta牡馬 と完璧配合になる繁殖牝馬の,牡馬牝馬の組み合わせを探る
    #返り値は牡馬牝馬の名前の組み合わせの名前をテキストで
    def search_cross_cross(self , sta ):
        print('in search cross cross')
        migoto_pair = '\n\n\n牡馬{}と見事配合が成立する牡馬ｘ牝馬の組み合わせ...\n\n'.format(sta.name)#探索した組み合わせをテキストで...見事
        perfect_pair = '\n\n\n牡馬{}と完璧配合が成立する牡馬ｘ牝馬の組み合わせ...\n\n'.format(sta.name)#探索した組み合わせをテキストで...完璧
        m_flg = 0
        p_flg = 0#テキスト分岐用フラグ

        chk_lst_s = []#検索レア度下限をチェックしてリストを作る...牡馬
        chk_lst_b = []#検索レア度下限をチェックしてリストを作る...牝馬

        for s in ds.stallions:#イテレートする馬のリストを作る
            if s.rare >= ds.S_LIMIT and sta.name != s.name:#自身をリストから除外
                chk_lst_s.append(s)#番号をリストに保存
        for b in ds.broodmares:#イテレートする馬のリストを作る
            if b.rare >= ds.B_LIMIT:
                chk_lst_b.append(b)

        #検索
        for s in chk_lst_s:
            for b in chk_lst_b:
                tmphorse= s.make_horse_to_broodmare(b)#ｓとｂで馬を作る
                #tmphorse がstaと見事、または完璧なるのかの判定
                if ds.search_great( tmphorse.omoshiro , sta.migoto ):#まずは見事か判定
                    if ds.search_funny( tmphorse.omoshiro + sta.omoshiro ):#なおかつ面白なら完璧
                        p_flg = 1
                        perfect_pair += '{}.{}  x  {}.{}\n\n'.format( s.rare , s.name , b.rare , b.name)
                    else:
                        m_flg = 1
                        migoto_pair += '{}.{}  x  {}.{}\n\n'.format( s.rare , s.name , b.rare , b.name)
        
        if p_flg == 0:
            perfect_pair += '無し\n\n\n\n'
        if m_flg == 0:
            migoto_pair += '無し\n\n\n\n'
        return perfect_pair + migoto_pair


    #上記関数の牝馬から検索をかけるバージョン
    #引数bro牝馬 と完璧配合になる種牡馬の,牡馬牝馬の組み合わせを探る
    #返り値は牡馬牝馬の名前の組み合わせの名前をテキストで
    def search_cross_cross_broodmare(self , bro ):
        print('in search cross cross broodmare')
        migoto_pair = '\n\n\n牝馬{}と見事配合が成立する牡馬ｘ牝馬の組み合わせ...\n'.format(bro.name)#探索した組み合わせをテキストで...見事
        perfect_pair = '\n\n\n牝馬{}と完璧配合が成立する牡馬ｘ牝馬の組み合わせ...\n'.format(bro.name)#探索した組み合わせをテキストで...完璧




        m_flg = 0
        p_flg = 0#テキスト分岐用フラグ

        chk_lst_s = []#検索レア度下限をチェックしてリストを作る...牡馬
        chk_lst_b = []#検索レア度下限をチェックしてリストを作る...牝馬

        for s in ds.stallions:#イテレートする馬のリストを作る
            if s.rare >= ds.S_LIMIT and bro.name != s.name:#自身をリストから除外
                chk_lst_s.append(s)#番号をリストに保存
        for b in ds.broodmares:#イテレートする馬のリストを作る
            if b.rare >= ds.B_LIMIT:
                chk_lst_b.append(b)

        #検索
        for s in chk_lst_s:
            for b in chk_lst_b:
                tmphorse= s.make_horse_to_broodmare(b)#ｓとｂで馬を作る
                #tmphorse がbroと見事、または完璧なるのかの判定
                if ds.search_great( tmphorse.migoto , bro.omoshiro ):#まずは見事か判定
                    if ds.search_funny( tmphorse.omoshiro + bro.omoshiro ):#なおかつ面白なら完璧
                        p_flg = 1
                        perfect_pair += '{}.{} x {}.{}\n\n'.format( s.rare , s.name , b.rare , b.name)
                    else:
                        m_flg = 1
                        migoto_pair += '{}.{} x {}.{}\n\n'.format( s.rare , s.name , b.rare , b.name)
        
        if p_flg == 0:
            perfect_pair += '無し\n\n\n\n'
        if m_flg == 0:
            migoto_pair += '無し\n\n\n\n'
        return perfect_pair + migoto_pair



    def set_list_b(self):#繁殖牝馬を選択するためのリスト作成
        st_list = []#リストに表示するための文字列のリスト

        tmp = ''
        #リストを一旦クリアする処理
        lastnum = self.blist.index( tk.END )
        self.blist.delete( 0 , lastnum )
        
        for i,horse in enumerate( ds.broodmares ):
            #リストに表示する文字列を作成していく
            tmp = '{:>03}:R{} {:<15} --'.format(i , horse.rare , horse.name)
            tmp += '{0[0]} {0[1]} {0[2]} {0[3]} -- {1[0]} {1[1]} {1[2]} {1[3]}'.format(horse.omoshiro , horse.migoto)
            st_list.append(tmp)
        for i in range( len( st_list ) ):#登場パターンをボックスにセット
            self.blist.insert ( i , st_list[i] )
        



    def set_list_s(self):#種牡馬を選択するためのリスト作成
        st_list = []#リストに表示するための文字列のリスト

        tmp = ''
        lastnum = self.slist.index( tk.END )
        self.slist.delete( 0 , lastnum )
        
        for i,horse in enumerate( ds.stallions ):
            #リストに表示する文字列を作成していく
            tmp = '{:>03}:R{} {:<15} --'.format(i , horse.rare , horse.name)
            tmp += '{0[0]} {0[1]} {0[2]} {0[3]} -- {1[0]} {1[1]} {1[2]} {1[3]}'.format(horse.omoshiro , horse.migoto)
            st_list.append(tmp)

        for i in range( len( st_list ) ):#登場パターンをボックスにセット
            self.slist.insert ( i , st_list[i] )



#自家製馬を作成するフレーム
class originbrowser( mainbrowser ):
    def __init__( self , frame ):
        super().__init__( frame )
        #追加変更のウィジェット
        self.newhorse = self.set_blankhorse()#新馬用にデフォルトで空のデータ馬を作成
        self.newname = tk.StringVar()
        self.set_widgets( frame )
        self.set_list_s()#種牡馬の一覧をリストにセット
        self.set_list_b()#繁殖牝馬の一覧をリストにセット


    def set_widgets(self , frame ):
        self.font_button = Ft.Font(size = 9 , family = 'Arial' , weight = 'bold' )
        self.font_text = Ft.Font(size = 8 , family = 'Arial')
        
        self.f1 = tk.Frame( frame , relief=tk.RIDGE, bd=2 )
        #種牡馬表示リスト
        self.slist = tk.Listbox( self.f1 , height = '8' , width = '60' , selectmode = 'SINGLE' )
        self.sbar = tk.Scrollbar(self.f1, orient = 'v', command = self.slist.yview )
        self.slist.configure(yscrollcommand = self.sbar.set)
        #牝馬表示リスト
        self.blist = tk.Listbox( self.f1 , height = '8' , width = '60' , selectmode = 'SINGLE' )
        self.bbar = tk.Scrollbar(self.f1, orient = 'v', command = self.blist.yview )
        self.blist.configure(yscrollcommand = self.bbar.set)

        self.btstallions = tk.Button(self.f1, text='牡馬として保存', bg='cyan2',font = self.font_button ,
                             bd=2 , padx =5 , command = self.make_s)
        self.btbroodmare = tk.Button(self.f1, text='牝馬として保存', bg='yellow2',font = self.font_button ,
                             bd=2 , padx =5 , command = self.make_b)
        self.showinfo = tk.Button(self.f1, text='データ確認', bg='red',font = self.font_button ,
                             bd=2 , padx =5 , command = self.newhorse_show )
        #名前入力欄
        self.ent01 = tk.Entry(self.f1 , textvariable = self.newname , width = 20)
        

        self.slist.grid( row = 1 , column = 0 , sticky = 'ns')
        self.sbar.grid( row = 1 , column = 0 , sticky = 'ns' + 'e')

        self.btstallions.grid(row = 2 , column = 0)
        self.btbroodmare.grid(row = 3 , column = 0)
        self.showinfo.grid(row = 2 , column = 1 )
        self.ent01.grid(row = 3 , column = 1)

        self.blist.grid( row = 4 , column = 0 , sticky = 'ns')
        self.bbar.grid( row = 4 , column = 0 , sticky = 'ns' + 'e')

        self.firstwindow = ScrolledText(self.f1 , height = '64' , font = self.font_text ,
                                        width = '48' ,padx = '3' , pady = '3' , relief = 'groove')
        self.firstwindow.grid( row = 1 , column = 2, rowspan = 4)

        #自家製削除用に右クリック対応をバンドル
        self.slist.bind('<Button-3>', self.delete_origin )#削除機能テスト。別窓開く
        self.blist.bind('<Button-3>', self.delete_origin )#削除機能テスト。別窓開く


    #デフォルト用のからデータの馬クラスをインスタンスして返す
    def set_blankhorse(self):
        b_data = ['空馬','1']
        for i in range(0,15):
            b_data.append('')
        for i in range(0,15):
            b_data.append('Herod')
        return horse(b_data)



    def newhorse_show(self):
        current_s = int( self.slist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
        current_b = int( self.blist.get( tk.ACTIVE )[:3] )#リストの選択された行が何行目かを取得 0スタート
        tmp = ''
        flg = 0
        
        self.newhorse = ds.stallions[current_s].make_horse_to_broodmare( ds.broodmares[current_b] )#馬作成

        self.firstwindow.delete( 0.0 , tk.END )
        
        if ds.tmpcheck == 0:#新馬を保存するかどうかのフラグ状態を確認
            txt = """*** 現在自家製馬は データベースに保存する になっています ***\n
            状態を変更する場合はメニューを確認してください \n\n"""
        elif ds.tmpcheck == 1:
            txt = """*** 現在自家製馬は データベースに保存しない になっています ***\n
            テンポラリに一時保存されますので、アプリ終了後データは消えます。
            状態を変更する場合はメニューを確認してください \n\n"""



        #選択中の2頭を組み合わせた際のインブリードクロスを表示する
        txt += 'インブリード情報\n\n'
        txt += '        種牡馬 {} \n\n'.format( ds.stallions[current_s].name )
        self.firstwindow.insert( tk.END , txt )
        for i in range( 0 , 15 ):
            flg = 0
            tmp = ds.get_inbreed( ds.stallions[current_s].blood[i] )#血統名を渡して、インブリード効果があるのならその効果名が返ってくる
            txt = '{:<4} {}    {}\n'.format( ds.fmnew[i] , ds.stallions[current_s].blood[i] , tmp )
            #牝馬と血統がクロスしていればヒ表示タグを付加する処理
            for j in range( 0 , 15 ):
                if ds.stallions[current_s].blood[i] == ds.broodmares[current_b].blood[j]:
                    flg = 1
            if flg == 1:
                self.firstwindow.insert( tk.END , txt , 'red' )
            else:
                self.firstwindow.insert( tk.END , txt )
        
        txt = '\n        繁殖牝馬 {}\n\n'.format( ds.broodmares[current_b].name)
        self.firstwindow.insert( tk.END , txt )
        for i in range( 0 , 15):
            flg = 0
            tmp = ds.get_inbreed(ds.broodmares[current_b].blood[i])
            txt = '{:<4} {}    {}\n'.format( ds.fmnew[i] , ds.broodmares[current_b].blood[i] , tmp )
            for j in range( 0 , 15 ):
                if ds.broodmares[current_b].blood[i] == ds.stallions[current_s].blood[j]:
                    flg = 1
            if flg == 1:
                self.firstwindow.insert( tk.END , txt , 'red' )
            else:
                self.firstwindow.insert( tk.END , txt )
        self.firstwindow.tag_config( 'red' , underline = 1 , background = '#ff9999')
        #組み合わせた馬のデータを表示
        txt = '\n\n組み合わせたらできる馬は...\n\n' + self.newhorse.show_selfdata()
        self.firstwindow.insert( tk.END , txt )
        #名前入力欄に名前をセット
        self.newname.set( self.newhorse.name )
        






    def make_b(self):#牝馬をデータベースに登録する処理
        self.newhorse.name = self.newname.get()
        self.add_origin(self.newhorse , 'f' )

    def make_s(self):#牡馬をデータベースに登録する処理
        self.newhorse.name = self.newname.get()
        self.add_origin(self.newhorse , 'm' )


    def add_origin(self , dataclass , flg):
        #引数の馬データクラスを、sqliteに書き込むデータ形式に変換する
        horsedata = []
        horsedata.append(dataclass.name)
        horsedata.append(dataclass.rare)
        for i in range(0,15):
            horsedata.append(dataclass.blood[i])
        for i in range(0,15):
            horsedata.append(dataclass.pedigree[i])

        if ds.tmpcheck == 0:#データベース保存する場合
            conn = sqlite3.connect( ds.DB_FILE )#ファイル名を入力
            curs = conn.cursor()
            if flg == 'm':#牡馬
                sql = """INSERT INTO origin_sdata VALUES ( ? , ? ,
                                            ? , ? , ? , ? , ? , ? , ? , ? ,
                                            ? , ? , ? , ? , ? , ? , ? ,
                                            ? , ? , ? , ? , ? , ? , ? , ? ,
                                            ? , ? , ? , ? , ? , ? , ? )"""
                curs.execute(sql,horsedata)
            elif flg == 'f':#牝馬
                sql = """INSERT INTO origin_bdata VALUES ( ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? , ? ,
                                        ? , ? , ? , ? , ? , ? , ? )"""
                curs.execute(sql,horsedata)
            conn.commit()
            conn.close()   
            self.firstwindow.insert( tk.END , '\n新馬をデータベースに追加したので、プルダウンメニューからデータ更新を行ってください\n')

        elif ds.tmpcheck == 1:#データベースに保存せずtmpに一時保存の場合
            self.newhorse.name = 'T.' + self.newhorse.name#テンポラリを表す記号を名前に追加
            if flg == 'm':
                ds.st_tmp.append( copy.copy(self.newhorse) )#テンポラリリストに追加
            elif flg == 'f':
                ds.br_tmp.append( copy.copy(self.newhorse) )#テンポラリリストに追加
            self.firstwindow.insert( tk.END , """新馬をテンポラリに追加しました。\n\n
                                    データを残したい場合にはメニューのチェックを外してください\n
                                    かならずプルダウンメニューからデータ更新を行ってください\n""")



    #テンポラリに指定の馬の組み合わせで作られた馬を登録するメソッド
    #引数 flg...基礎になるのが牡馬か牝馬か   couplelist.種牡馬番号、牝馬番号の組み合わせタプルのリスト
    @classmethod
    def add_tmphorse_from_other(self , flg , couplelist ):
        tmphorse = self.set_blankhorse( self )
        for c in couplelist:
            tmphorse = ds.stallions[ c[0] ].make_horse_to_broodmare(ds.broodmares[ c[1] ] )
            tmphorse.name = 'T.' + tmphorse.name#テンポラリを表す記号を名前に追加
            if flg == 's':
                ds.st_tmp.append( copy.copy(tmphorse) )#テンポラリリストに追加
            elif flg == 'b':
                ds.br_tmp.append( copy.copy(tmphorse) )#テンポラリリストに追加





    #自家製馬の削除機能
    def delete_origin( self , event ):
        w = event.widget#右クリックされたウィジェット取得
        if w == self.slist:#種牡馬リスト上で右クリック
            flg = 's'
        elif w == self.blist:
            flg = 'b'
        #ウィンドウをポップアップ
        pop = tk.Toplevel()
        pop.title('自家製馬の削除')
        tmplist = tk.Listbox( pop , height = '12' , width = '30' , selectmode = 'SINGLE' )
        sbar = tk.Scrollbar(pop, orient = 'v', command = tmplist.yview )
        tmplist.configure(yscrollcommand = sbar.set)
        tmplist.grid( row = 0 , column = 0 , columnspan = 2, sticky = 'ns')
        sbar.grid( row = 0 , column = 0 , columnspan = 2 , sticky = 'ns' + 'e')
        
        h_namelist = self.tmplist_set(flg,tmplist)#リストに自家製馬の牡馬か牝馬どちらかの名前をリストにセットする

        exebutton = tk.Button( pop , text = '削除実行' ,
                              command = self.call_delete( flg , tmplist , h_namelist ) )#リストの選択された行が何行目かを取得 0スタート ) )
        canbutton = tk.Button( pop , text = 'キャンセル' , command = pop.destroy )
        exebutton.grid(row = 1 , column = 0)
        canbutton.grid(row = 1 , column = 1)
        

    def tmplist_set(self , flg , listname):
        if flg == 's':
            dat = 'origin_sdata'
        elif flg == 'b':
            dat = 'origin_bdata'

        list_origin = []
        st_list = []
        ret_namelist = []
        conn = sqlite3.connect(ds.DB_FILE)
        curs = conn.cursor()
        sql = "select * from {} order by rarepoint desc,horsename asc".format(dat)
        curs.execute( sql )
        list_origin = curs.fetchall()#馬データ
        conn.commit()
        conn.close()  
        
        for i , s in enumerate(list_origin):
            tmp = '{:>03}:R{} {:<15}'.format(i , s[1] , s[0])
            st_list.append(tmp)
            ret_namelist.append(s[0])

        for i in range( 0,len( st_list ) ):#登場パターンをボックスにセット
            listname.insert ( i , st_list[i] )

        return ret_namelist

    #削除処理
    #引数 name 馬の名前    flg 's'or'b' 自家製の牡馬牝馬どちらなのか
    def call_delete(self , flg , l_obj , namelist ):
        def t():
            if flg == 's':
                dat = 'origin_sdata'
            elif flg == 'b':
                dat = 'origin_bdata'

            name = namelist[ l_obj.curselection()[0] ]
            #print('check name',name)
            if Mb.askokcancel(title = '自家製馬の削除',message = '{}をデータベースから削除しますがよろしいですか？'.format(name)):
                try:
                    conn = sqlite3.connect(ds.DB_FILE)
                    curs = conn.cursor()
                    sql = 'delete from {} where horsename = "{}"'.format(dat,name)
                    curs.execute( sql )
                    conn.commit()
                    conn.close()  

                except sqlite3.OperationalError:
                    print('sql:',sql)
                    print('エラー{}がみつからないっぽい？'.format(name) )
        return t


#A-B-CD検索のフレームクラス
#まず締めの種牡馬を決め、見事完璧になる母父と、母母の父と母を探索するクラス
class abcdbrowser(originbrowser):
    def __init__( self , frame ):
        super().__init__( frame )
        #追加変更のウィジェット
        
        
        self.set_widgets( frame )
        
        self.set_list_first()#種牡馬のリストをセット
        
        self.searchbld = ['','','','']
        self.check_omo = ['','','','','','','','']#追加
        self.mflist = []#母父候補の番号を収めたリスト
        self.fnumber = 0#現在選択中の父候補の種牡馬番号
        self.mmlist = []#母母候補の番号を収めたリスト
        self.showflg = 0#母系か父系のどちらの検索を行っているのかを示すflg 0 -> 母父 : 1 -> 母母

        self.mf_horse = []#母父候補の馬データクラスのリスト
        self.mm_horse = []#母母候補の馬データクラスのリスト
        

        

    def set_widgets(self , frame ):
        self.font_text = Ft.Font(size = 8 , family = 'Arial')
        
        self.f1 = tk.Frame( frame , relief=tk.RIDGE, bd=2 )
        #種牡馬表示リスト
        self.firstlist = tk.Listbox( self.f1 , height = '8' , width = '65' , selectmode = 'SINGLE' )
        self.firstbar = tk.Scrollbar(self.f1, orient = 'v', command = self.firstlist.yview )
        self.firstlist.configure(yscrollcommand = self.firstbar.set)
        #牝馬表示リスト
        self.secondlist = tk.Listbox( self.f1 , height = '8' , width = '65' , selectmode = 'SINGLE' )
        self.secondbar = tk.Scrollbar(self.f1, orient = 'v', command = self.secondlist.yview )
        self.secondlist.configure(yscrollcommand = self.secondbar.set)

        self.btstart = tk.Button(self.f1, text='1.種牡馬決定', bg='chocolate1',
                             bd=2 , padx =5 , command = self.set_first)
        self.btstallions = tk.Button(self.f1, text='2.母父をリストに表示', bg='chocolate2',
                             bd=2 , padx =5 , command = self.call_second_list('s') )
        self.btbroodmare = tk.Button(self.f1, text='2.母母をリストに表示', bg='chocolate3',
                             bd=2 , padx =5 , command = self.call_second_list('b') )
        self.btshowinfo = tk.Button(self.f1, text='3.系統データ確認', bg='plum1',
                             bd=2 , padx =5 , command = self.call_second_show )

        self.deep = tk.BooleanVar()#多重検索を行うかの機能を追加
        self.deep.set(False)
        self.deep_check = tk.Checkbutton(self.f1 , text = 'B-CDの配合も検索（時間かかるかも）', variable = self.deep,
                                          onvalue = True , offvalue = False )

        

        self.firstlist.grid( row = 1 , column = 0 , columnspan = 3 ,sticky = 'ns')
        self.firstbar.grid( row = 1 , column = 3 , sticky = 'ns' + 'e')

        self.btstart.grid(row = 2 , column = 0)
        self.btstallions.grid(row = 3 , column = 0)
        self.btbroodmare.grid(row = 3 , column = 1)
        self.btshowinfo.grid(row = 5 , column = 0 )
        self.deep_check.grid(row = 6 , column = 0 )
        
        self.secondlist.grid( row = 4 , column = 0 , columnspan = 3 ,sticky = 'ns')
        self.secondbar.grid( row = 4 , column = 3 , sticky = 'ns' + 'e')

        self.firstwindow = ScrolledText(self.f1 , height = '70' , font = self.font_text ,
                                        width = '60' ,padx = '3' , pady = '3' , relief = 'groove')
        self.firstwindow.grid( row = 1 , column = 4, rowspan = 6)


    #選択された種牡馬の見事血統をチェックする。ついでに完璧配合が可能かどうかも表示
    def set_first(self):
        
        c = int( self.firstlist.get( tk.ACTIVE )[:3] )#リストから選択された、父になる種牡馬の基本となる馬の番号
        self.fnumber = c

        self.firstwindow.delete( 0.0 , tk.END )
        txt = ds.stallions[c].name + '\n\n'   
        txt += self.ret_bloodtxt_father( ds.stallions[c] )
        if ds.search_funny ( ds.stallions[c].omoshiro + ds.stallions[c].migoto ) == True:#完璧可能かチェック
            txt += '\n完璧配合が可能な種牡馬です\n\n'
        txt += '\n\n見事or完璧な配合に必要な系統は... {0[0]} {0[1]} {0[2]} {0[3]} \n\n'.format(ds.stallions[c].migoto)
        txt += '候補になる母父(または母母)をリストにセットするので、2ボタンでどちらかを選択してください\n\n'
        self.firstwindow.insert( tk.END , txt )


    #母父、または母母候補を作成するためのメソッド呼び出し
    #引数's'or'b'で牡馬か牝馬か
    def call_second_list(self,flg):
        def t():
            c = int( self.firstlist.get( tk.ACTIVE )[:3] )
            if flg == 's':
                self.set_mf_list( ds.stallions[c] )
            elif flg == 'b':
                self.set_mm_list( ds.stallions[c] )
            
        return t


    #最終的な配合検索処理メソッドを呼び出す。
    #引数で馬データを渡したいので設置
    def call_second_show(self):
        c = int( self.firstlist.get( tk.ACTIVE )[:3] )
        self.second_show( ds.stallions[c] )
        


    #候補となる母父の検索とリストの作成表示
    def set_mf_list(self , horse ):
        #mflistには、種牡馬の番号と、残りの必要な系統2種類が収められた配列が返ってくる
        self.mf_horse = self.get_mflist( horse )
        self.set_list_second( self.mf_horse )
        self.showflg = 0#母父選択状態を示すフラグ


    #候補となる母父の検索
    #引数は基本の種牡馬データクラス
    #返り値は対象馬データクラスのリスト
    def get_mflist(self , horse ):
        readhorse_s = []#候補のリスト番号
        retobj = []
        #self.searchbld を参照して該当する母父をリストアップする
        for i in range( len(ds.stallions) ):#種牡馬をイテレートして、レア度制限より上の種牡馬番号を抽出
            if ds.stallions[i].rare >= ds.S_LIMIT:
                readhorse_s.append(i)

        for i in readhorse_s:
            #検索対象牡馬の母になった時の面白系統が、引数種牡馬の見事系統に含まれているか
            if ds.stallions[i].omoshiro[0] in horse.migoto and ds.stallions[i].omoshiro[2] in horse.migoto:
                #母父の面白が同じ、かつsearchbldが異なる4系統ならば見事配合が不可能なので登録しない
                if self.chk_bldcount(horse.migoto) == 4 and ds.stallions[i].omoshiro[0] == ds.stallions[i].omoshiro[2]:
                    pass
                else:
                    retobj.append( ds.stallions[i] )#対象馬の馬データクラスをリストに追加

        return retobj


    #候補となる母母の検索とリストの作成表示
    def set_mm_list(self, horse ):
        #mflistには、牝馬の番号が返ってくる
        self.mm_horse = self.get_mmlist( horse )
        self.set_list_second( self.mm_horse )
        self.showflg = 1#母母選択状態を示すフラグ


    #セカンドリスト作成のための牝馬のリストを作成
    #返り値には馬のデータクラスを収めたリスト
    def get_mmlist(self , horse ):
        readhorse_b = []
        retobj = []
        #self.searchbld を参照して該当する母父をリストアップする
        for i in range( len( ds.broodmares ) ):#種牡馬をイテレートして、検索レア度制限より上の牝馬の番号を抽出
            if ds.broodmares[i].rare >= ds.B_LIMIT:
                readhorse_b.append(i)

        for i in readhorse_b:
            if ds.broodmares[i].omoshiro[0] in horse.migoto and ds.broodmares[i].omoshiro[2] in horse.migoto:
                #母母の面白が同じ、かつsearchbldが異なる4系統ならば見事配合が不可能なので登録しない
                if self.chk_bldcount(horse.migoto) == 4 and ds.broodmares[i].omoshiro[0] == ds.broodmares[i].omoshiro[2]:
                    pass
                else:
                    retobj.append( ds.broodmares[i] )

        return retobj



    def chk_bldcount(self , blist ):#blist が何種類の系統なのかを数えて返す
        bloodlist = ('Ec','Fa','Hmp','Her','Him','ND','Nas','Nea','Mach',
                 'Sts','Swn','Pha','RC','Ted','Tom')
        ret = 0
        for i in bloodlist:
            for j in blist:
                if i == j:
                    ret += 1
                    break
        return ret


    #見事配合可能な残りの2系統の取りうる組み合わせを探索する
    #引数　searchbld -> 見事配合4種のリスト    b0,b1 -> 確定の2系統 
    def lesssearch(self , searchbld , b0 , b1 ):
        retobj = []
        rettmp = []
        returnobj = []
        tmpto = ['','','','']#繁殖牝馬の面白系統テンポラリ
        tmpto[0] = b0
        tmpto[1] = b1

        for b2 in searchbld:
            tmpto[2] = b2
            for b3 in searchbld:
                tmpto[3] = b3
                if ds.search_great( searchbld , tmpto ):
                    rettmp.append(b2)
                    rettmp.append(b3)
                    retobj.append( copy.copy(rettmp) )
                    del rettmp[:]
        #retobj から、ダブっている組み合わせを削除する。順番が入れ替わっただけのものはダブリとして扱わない
        #print(retobj)
        for i in retobj:
            if i not in returnobj:
                returnobj.append(i)
        #print(returnobj)
        return returnobj


    #最終的なインブリード情報を表示
    #引数horseは大元の検索対象の種牡馬データクラス
    def second_show(self , horse ):
        self.firstwindow.tag_config( 'blue' , underline = 1 , background = '#6666ff')
        less = []#見事配合成立のための、母母または母父によって2種類が決まった時の残りの2系統を探索するためのリスト
        doflg = 0
        check_s_list = []#完璧配合チェック用の馬番号を入れるリスト
        check_b_list = []
        
        #リストが空でないか、きちんとセットされているかチェック
        if (self.showflg == 0 and len(self.mf_horse) != 0) or (self.showflg == 1 and len(self.mm_horse) != 0):
            doflg = 1
        
        if doflg != 0:#問題ないようなら検索開始
            sc = int( self.secondlist.get( tk.ACTIVE )[:3] )#セカンドリストの選択された母父または母母候補のリスト番号を取得
            
            self.firstwindow.delete( 0.0 , tk.END )
            txt = '検索の元の馬 ' + horse.name + '\n\n'   
            txt += self.ret_bloodtxt_father( horse )
            txt += '\n\n見事or完璧な配合に必要な系統は... {0[0]} {0[1]} {0[2]} {0[3]} \n\n\n'.format( horse.migoto )
            self.firstwindow.insert ( tk.END , txt )
            
            if self.showflg == 0:#リストが父系
                #完璧配合チェック用の配列に系統をセットする
                self.check_omo[4] = self.mf_horse[sc].omoshiro[0]
                self.check_omo[5] = self.mf_horse[sc].omoshiro[2]#父父の種牡馬作成時の面白チェック用の系統二つ
                
                txt = '\n\n    母父の持つ系統  \n'
                self.firstwindow.insert ( tk.END , txt )
                txt = '{}  '.format(self.mf_horse[sc].omoshiro[0])
                self.firstwindow.insert ( tk.END , txt , 'blue')
                txt = '{}  '.format(self.mf_horse[sc].omoshiro[1])
                self.firstwindow.insert ( tk.END , txt )
                txt = '{}  '.format(self.mf_horse[sc].omoshiro[2])
                self.firstwindow.insert ( tk.END , txt , 'blue')
                txt = '{}'.format(self.mf_horse[sc].omoshiro[3])
                self.firstwindow.insert ( tk.END , txt )
                txt = '\n    母父の持つインブリード血統\n\n'
                self.firstwindow.insert ( tk.END , txt )
                
                self.ret_bloodtxt_motherfather( self.mf_horse[sc] , horse.blood )#母父(又は母母)のインブリードを表示する
                #完璧配合作成のために必要な残りの系統を取得する.
                #返り値lessはリストで、系統の名前
                less = self.lesssearch( horse.migoto , self.mf_horse[sc].omoshiro[0] , self.mf_horse[sc].omoshiro[2] )
                
            elif self.showflg == 1:#リストが母系
                #完璧配合チェック用の配列に系統をセットする
                self.check_omo[4] = self.mm_horse[sc].omoshiro[0]
                self.check_omo[5] = self.mm_horse[sc].omoshiro[2]#父父の種牡馬作成時の面白チェック用の系統二つ
                
                txt = '\n\n    母母の持つ系統 \n'
                self.firstwindow.insert ( tk.END , txt )
                txt = '{}  '.format( self.mm_horse[sc].omoshiro[0] )
                self.firstwindow.insert ( tk.END , txt , 'blue' )
                txt = '{}  '.format( self.mm_horse[sc].omoshiro[1] )
                self.firstwindow.insert ( tk.END , txt )
                txt = '{}  '.format( self.mm_horse[sc].omoshiro[2] )
                self.firstwindow.insert ( tk.END , txt , 'blue' )
                txt = '{}  '.format( self.mm_horse[sc].omoshiro[3] )
                self.firstwindow.insert ( tk.END , txt )
                
                txt = '\n    母母の持つインブリード血統\n\n'                
                self.firstwindow.insert ( tk.END , txt ) 
                self.ret_bloodtxt_motherfather( self.mm_horse[sc] , horse.blood )#母母のインブリードを表示する
                #完璧配合作成のために必要な残りの系統を取得する.
                #返り値lessはリストで、系統の名前
                less = self.lesssearch( horse.migoto , self.mm_horse[sc].omoshiro[0] , self.mm_horse[sc].omoshiro[2] )


            #完璧配合成立な残りに系統になりうる組み合わせのサーチ            
            if len(less) != 0:#一覧をひとまず表示
                txt = '\n\n\n--- 見事完璧成立に必要な、残りの2系統の組み合わせ ---\n\n\n'
                for pair in less:
                    txt += ' [ {} - {} ] \n'.format( pair[0] , pair[1] )
                txt += 'の{} 通り\n\n'.format( len(less) )
                self.firstwindow.insert ( tk.END , txt )
                for pair in less:
                    txt = '========================================================\n' 
                    txt += '========================================================\n' 
                    txt += ' [ {} - {} ] の組み合わせになる牡馬と牝馬\n\n\n'.format( pair[0] , pair[1] )
                    self.firstwindow.insert ( tk.END , txt ,'purple')
                    self.firstwindow.tag_config( 'purple' , underline = 1 , background = '#ff00ff')

                    check_s_list , check_b_list = self.search_mm( pair[0] , pair[1] , horse.blood )#2系統組み合わせのサーチと情報表示

                    if len(check_s_list) != 0 and len(check_b_list) != 0:#返ってきたリストが空白でなければ完璧配合チェック
                        if self.showflg == 0:#母父ｘ（CｘD）の組み合わせ
                            self.check_omoshiro(self.showflg , self.mf_horse[sc] , check_s_list , check_b_list , horse.omoshiro )
                        elif self.showflg == 1:#(CｘD） x 母母の組み合わせ
                            self.check_omoshiro(self.showflg , self.mm_horse[sc] , check_s_list , check_b_list , horse.omoshiro )
            else:#組み合わせが発見できなかった場合のテキスト表示
                txt = '\n\n\n--- 見事完璧成立はむりっぽい？レア度を下げて再検索すれば出てくるかも ---\n\n'
                self.firstwindow.insert ( tk.END , txt ) 



    #flg -> 0 ３頭の組み合わせ(母父　ｘ　（母母父ｘ母母母） )と、大元の種牡馬が面白になっているのかのチェック
    #なっていれば完璧配合、なっていなければ見事配合
    #flg -> 1 ３頭の組み合わせ(（母父父ｘ母父母） x 母母 )と、大元の種牡馬が面白になっているのかのチェック
    #flgは...numの番号の馬が 0_牡馬 x (牡馬x牝馬) ,1_ (牡馬x牝馬) X 牝馬
    #basemigotoは、大元の種牡馬の見事系統リスト
    def check_omoshiro( self , flg , horse , slist , blist , baseomoshiro ):
        self.firstwindow.tag_config( 'blue' , underline = 1 , background = '#9999ee')
        searching = 0#完璧検索にヒットしたかどうか
        txt = '\nその中で完璧配合になる組み合わせ...\n\n'
        self.firstwindow.insert ( tk.END , txt )

        tmp_omo = ['','','','']
        if flg == 0:
            tmp_omo[0] = horse.omoshiro[0]
            tmp_omo[1] = horse.omoshiro[2]
            for s in slist:
                tmp_omo[2] = ds.stallions[s].omoshiro[0]
                for b in blist:
                    tmp_omo[3] = ds.broodmares[b].omoshiro[0]
                    #見事系統の組み合わせの組み合わせの中から完璧判定を行う
                    if ds.search_funny(baseomoshiro + tmp_omo ):
                        searching = 1
                        txt = '{} x ( {} - {} )\n\n'.format( horse.name ,ds.stallions[s].name ,
                                                       ds.broodmares[b].name)
                        #多重配合理論適合チェック
                        if self.deep.get():
                            txt += self.perfect_show( 's' , horse , ds.stallions[s] ,ds.broodmares[b])
                        self.firstwindow.insert ( tk.END , txt )
        elif flg == 1:
            tmp_omo[0] = horse.omoshiro[0]
            tmp_omo[1] = horse.omoshiro[2]
            for s in slist:
                tmp_omo[2] = ds.stallions[s].omoshiro[0]
                for b in blist:
                    tmp_omo[3] = ds.broodmares[b].omoshiro[0]
                    #見事系統の組み合わせの組み合わせの中から完璧判定を行う
                    if ds.search_funny( baseomoshiro + tmp_omo ):
                        searching = 1
                        txt = '( {} - {} ) x {}\n'.format( ds.stallions[s].name ,
                                                       ds.broodmares[b].name , horse.name )
                        #多重配合理論適合チェック
                        if self.deep.get():
                            txt += self.perfect_show( 'b' , horse , ds.stallions[s] ,ds.broodmares[b])
                        self.firstwindow.insert ( tk.END , txt )



        #完璧な組み合わせがなかった時のテキスト表示
        if searching == 0:
            txt = '\n\n完璧な配合になる組み合わせはありませんでした\n\n\n'
        else:
            #空白行挿入
            txt = '\n\n\n\n'
        self.firstwindow.insert ( tk.END , txt )



    #引数の系統に合致する馬を探索する
    #引数は探索対象の系統    sbld -> 牡馬の面白系統[0] bbld -> 牝馬の面白系統[0]
    #baseblood -> 検索の大元の馬の血統リスト
    def search_mm(self , sbld , bbld , baseblood ):
        slist = []#対象となる牡馬の番号
        blist = []#対象となる牝馬の番号

        for i in range( 0 , len(ds.stallions) ):#種牡馬をイテレートして、レア度制限より上の種牡馬番号を抽出
            if ds.stallions[i].rare >= ds.S_LIMIT:
                if sbld == ds.stallions[i].omoshiro[0]:
                    slist.append(i)
        #print(slist)
        for i in range( 0 , len(ds.broodmares) ):#種牡馬をイテレートして、レア度制限より上の繁殖牝馬番号を抽出
            if ds.broodmares[i].rare >= ds.B_LIMIT:
                if bbld == ds.broodmares[i].omoshiro[0]:
                    blist.append(i)


        #情報表示処理
        txt = '\n{} を持つ種牡馬...{} 頭\n\n'.format( sbld , len(slist) )
        self.firstwindow.insert ( tk.END , txt , 'blue') 
        if len(slist) != 0:    
            for i in slist:
                txt = '      {}\n'.format( ds.stallions[i].name )#名前
                self.firstwindow.insert ( tk.END , txt )
                self.ret_bloodtxt_mmfather('s' , ds.stallions[i] , baseblood )



        txt = '\n{} を持つ繁殖牝馬...{} 頭\n\n'.format( bbld , len(blist) )
        self.firstwindow.insert ( tk.END , txt , 'blue' ) 
        if len(blist) != 0:
            for i in blist:
                txt = '      {}\n'.format( ds.broodmares[i].name )#名前
                self.firstwindow.insert ( tk.END , txt )    
                self.ret_bloodtxt_mmfather('b' , ds.broodmares[i] , baseblood )
        self.firstwindow.tag_config( 'blue' , underline = 1 , background = '#6666ff')
        return slist,blist




    #種牡馬を選択するためのリスト作成
    def set_list_first(self):
        st_list = []#リストに表示するための文字列のリスト
        tmp = ''
        lastnum = self.firstlist.index( tk.END )
        self.firstlist.delete( 0 , lastnum )#一旦リストを削除
        
        for i,horse in enumerate( ds.stallions ):
            tmp = '{:>03} {:>15} {}'.format(str(i) , horse.name , horse.rare)
            tmp += '-- {0[0]} {0[1]} {0[2]} {0[3]} -- {1[0]} {1[1]} {1[2]} {1[3]}'.format( horse.omoshiro , horse.migoto)
            st_list.append(tmp)
        for i in range( len( st_list ) ):#文字列をボックスにセット
            self.firstlist.insert ( i , st_list[i] )   


    #母父を選択するためのリスト作成
    #引数は対象となる種牡馬のデータクラスが入ったリスト
    def set_list_second(self , h_list ):
        st_list = []#リストに表示するための文字列のリスト
        tmp = ''
        lastnum = self.secondlist.index( tk.END )
        self.secondlist.delete( 0 , lastnum )#リストの初期化

        for i,h in enumerate(h_list):
            tmp = '{:>03} {:>15} {} --牝馬時の面白系統 {} {} '.format( i , h.name ,
                   h.rare , h.omoshiro[0] , h.omoshiro[2])
            st_list.append(tmp)
        
        for i in range( len( st_list ) ):#登場パターンをボックスにセット
            self.secondlist.insert ( i , st_list[i] )  


    #母母を選択するためのリスト作成
    #引数は対象となる繁殖牝馬のデータクラスが入ったリスト
    def set_list_second_B(self , h_list ):
        st_list = []#リストに表示するための文字列のリスト
        tmp = ''
        lastnum = self.secondlist.index( tk.END )
        self.secondlist.delete( 0 , lastnum )

        for i,h in enumerate(h_list):
            tmp = '{:>03} {:>15} {} --牝馬時の面白系統 {} {} '.format( i , h.name ,
                   h.rare , h.omoshiro[0] ,h.omoshiro[2])
            st_list.append(tmp)
        
        for i in range( len( st_list ) ):#登場パターンをボックスにセット
            self.secondlist.insert ( i , st_list[i] )



    #渡された種牡馬データの血統のテキストを返す
    def ret_bloodtxt_father(self , horse ):
        rettxt = ''
        for i in range( 0 , 15):
            tmp = ds.get_inbreed( horse.blood[i])#血統名を渡して、インブリード効果があるのならその効果名が返ってくる
            rettxt += '{:<4} {}        {}\n'.format( ds.fmnew[i] , horse.blood[i] , tmp )
        return rettxt



    #引数 flg -> 's'or'b' (A-BC)型検索で、Aが牡馬か牝馬か。sta ->牡馬    bro ->牝馬
    #horse と、sta broで出来た馬になにかしら配合理論がついているかどうか、インブリードが発生しているのかのチェック
    #何もなければ'\n'何かしらの配合理論がせいりつするならその旨をテキストで
    def perfect_show(self , flg , horse , sta , bro ):
        txt = '\n'
        tmphorse = sta.make_horse_to_broodmare(bro)#テンポラリとしてstaとbroの馬を作成

        if flg == 's':
            if ds.search_great( tmphorse.omoshiro , horse.migoto ):
                if ds.search_funny ( tmphorse.omoshiro + horse.omoshiro ):
                    txt += '{} x ({}x{}) \nは完璧配合です\n\n\n'.format( horse.name , sta.name , bro.name )
                else:
                    txt += '{} x ({}x{}) \nは見事配合です\n\n\n'.format( horse.name , sta.name , bro.name )
            elif ds.search_good (tmphorse.omoshiro , horse.migoto ):
                txt += '{} x ({}x{}) \nはよくできた配合です\n\n\n'.format( horse.name , sta.name , bro.name )
            elif ds.search_funny ( tmphorse.omoshiro + horse.omoshiro ):
                txt += '{} x ({}x{}) \nは面白い配合です\n\n\n'.format( horse.name , sta.name , bro.name )
        elif flg == 'b':
            if ds.search_great( horse.omoshiro , tmphorse.migoto ):
                if ds.search_funny ( tmphorse.migoto + horse.omoshiro ):
                    txt += '({}x{}) x {} \nは完璧配合です\n\n\n'.format( sta.name , bro.name , horse.name )
                else:
                    txt += '({}x{}) x {} \nは見事配合です\n\n\n'.format( sta.name , bro.name , horse.name )
            elif ds.search_good ( horse.omoshiro , tmphorse.migoto ):
                txt += '({}x{}) x {} \nはよくできた配合です\n\n\n'.format( sta.name , bro.name , horse.name )
            elif ds.search_funny ( horse.omoshiro + tmphorse.omoshiro ):
                txt += '({}x{}) x {} \nは面白い配合です\n\n\n'.format( sta.name , bro.name , horse.name )
        return txt
            

            
            



    #渡された馬データの母父、または母母になった時の血統のテキストを抜き出して,表示する
    #引数 horse　は　母父（又は母母）の馬クラス base_inbreed は大元の種牡馬のインブリード血統名のリスト
    def ret_bloodtxt_motherfather(self , horse , baselist ):
        mf_inbreed = []#母父になった時の血統名8つ
        showlist = []
        fmlist = []#父母などの系統の何番目を表示させるのか

        if self.showflg == 0:#母父選択状態を示すフラグ
            showlist =  [0,0,1,2,5,8,9,12]#抽出するインブリード血統名の配列番号。先頭には自分の名前が入る
            fmlist = [0,1,2,3,4,5,6,7]#父母などの系統の何番目を表示させるのか
            for i in showlist:
                mf_inbreed.append( horse.blood[i] )
            mf_inbreed[0] = horse.name
        elif self.showflg == 1:#母母選択状態
            showlist = [0,1,2,5,8,9,12]
            fmlist = [8,9,10,11,12,13,14]#父母などの系統の何番目を表示させるのか
            for i in showlist:
                mf_inbreed.append( horse.blood[i] )


        for n,i in zip( fmlist , mf_inbreed):
            tmp = ds.get_inbreed( i )#血統名を渡して、インブリード効果があるのならその効果名が返ってくる
            txt = '      {:<4} {}        {}\n'.format( ds.fmnew[n] , i , tmp )
            flg = 0
            for j in baselist:
                if i == j:
                    flg = 1
                    break
            if flg == 1:
                self.firstwindow.insert( tk.END , txt , 'red' )
            else:
                self.firstwindow.insert( tk.END , txt )
        self.firstwindow.insert( tk.END , '\n\n' )
        self.firstwindow.tag_config( 'red' , underline = 1 , background = '#ff9999')




    #渡された番号の母母父、母母母、父父父、父母父(A-B-CDの C or D の時)の血統のテキストを返す
    #引数 horseblood　は　対象となる馬クラス base_inbreed は大元の種牡馬のインブリード血統名のリスト
    #flg 's' or 'b' は、対象となる馬が牡馬か牝馬かのフラグ(sの時はインブリードが4、bの時は3個分のテキスト表示となる)
    def ret_bloodtxt_mmfather(self , flg , horse , baselist ):
        showlist = []
        fmlist = []
        mf_inbreed = []#空白プラス 母母父になった時の血統名4つ(牝馬なら3つ)
        fmlist = []#父母などの系統の何番目を表示させるのか
        if flg == 's':
            #mf_inbreed.append(horse.name)
            if self.showflg == 1:#父父の血統を表示する時
                fmlist = [0,1,2,3,4]
                showlist = [0,0,1,2,8]#訂正
            elif self.showflg == 0:
                fmlist = [8,9,10,11]#母父
                showlist = [0,0,1,8]
                
        elif flg == 'b':
            if self.showflg == 1:#父母の血統を表示する時
                fmlist = [5,6,7]
                showlist = [0,1,8]
            elif self.showflg == 0:
                fmlist = [12,13,14]#母母
                showlist = [0,1,8]
            
        for i in showlist:
            mf_inbreed.append( horse.blood[i] )
        if flg == 's':
            mf_inbreed[0] = horse.name



        for n,i in zip( fmlist , mf_inbreed ):
            tmp = ds.get_inbreed( i )#血統名を渡して、インブリード効果があるのならその効果名が返ってくる
            txt = '      {:<4} {}        {}\n'.format( ds.fmnew[n] , i , tmp )
            flg = 0
            for j in baselist:
                if i == j:
                    flg = 1
                    break
            if flg == 1:
                self.firstwindow.insert( tk.END , txt , 'red' )
            else:
                self.firstwindow.insert( tk.END , txt )
        self.firstwindow.insert( tk.END , '\n' )
        self.firstwindow.tag_config( 'red' , underline = 1 , background = '#ff9999')




#おまけ
#系統、インブリード所持馬検索
#トップフレームで起動しようとするも、挙動が怪しいのでストップ中
class thirdframe():
    def __init__(self):
        self.mainframe = tk.Tk()
        self.setVar()
        self.setWidgets()
        
        
    #変数の設定
    def setVar(self):
        #topframe.data_inbreed_set()#他クラスからインブリード効果をコンフィグの辞書にセット
        #馬クラスを保持するリスト
        #ds.stallions = []
        #ds.broodmares = []
        
        #self.readdata_from_sql()
        #検索系統のチェック変数
        self.omo = []
        tmp = []
        for i in range(0,4):
            for j in range(0,15):
                tmp.append( tk.BooleanVar() )
                tmp[j].set(False)
            self.omo.append( copy.copy(tmp) )
            del tmp[:]

        self.dic_key1 = []#英語名インブリードリスト
        self.dic_key2 = []#全角かな名インブリードリスト
        self.inb_chk1 = []
        self.inb_chk2 = []
        #辞書のキーのリストを作成(和名、英語名で分ける)
        for k in ds.inbreed:
            if re.match(r'[a-zA-Z]+' , k) != None:
                self.dic_key1.append(k)
            else:
                self.dic_key2.append(k)
        self.dic_key1 = sorted(self.dic_key1)
        self.dic_key2 = sorted(self.dic_key2)

        for i in range( len(self.dic_key1) ):
            self.inb_chk1.append( tk.BooleanVar() )
            self.inb_chk1[i].set(False)
        for i in range( len(self.dic_key2) ):
            self.inb_chk2.append( tk.BooleanVar() )
            self.inb_chk2[i].set(False)


        self.bld_txt = ['Ec','Fa','Hmp','Her','Him','ND','Nas','Nea','Mach','Sts',
                    'Swn','Pha','RC','Ted','Tom']

    #画面の作成
    def setWidgets(self):
        #ラベル
        self.topLabel = tk.Label(self.mainframe , text='系統検索フレーム', font= (None, 15) )
        self.topLabel.grid(row = 0,column = 0,columnspan =2)
        #検索ボタン
        self.bt01 = tk.Button(self.mainframe, text='牡馬を検索', bg='cyan',
                             bd=2 , padx =6 , command = self.search_start('s') )
        self.bt01.grid(row = 2 , column = 0)
        self.bt02 = tk.Button(self.mainframe, text='牝馬を検索', bg='orchid1',
                             bd=2 , padx =6 , command = self.search_start('b') )
        self.bt02.grid(row = 2 , column = 1)
        #検索メニュー
        #系統検索
        m_title = ['面白1','面白2','面白3','面白4']
        
        self.bldmenu = []
        for i in range(0,4):
            self.bldmenu.append( tk.Menubutton( self.mainframe , width = 16 ,text = m_title[i],
                                            relief=tk.RIDGE  ) )
            
            self.bldmenu[i].grid(row = 3 , column = i )
            self.bldmenu[i].menu = tk.Menu(self.bldmenu[i] , tearoff = 0)
            for j in range(0,15):
                self.bldmenu[i].menu.add_checkbutton( label=self.bld_txt[j] , onvalue = True ,
                            offvalue = False , variable = self.omo[i][j] ,command = self.set_blood( (i,j) ) )

            self.bldmenu[i]['menu'] = self.bldmenu[i].menu

        #インブリード検索1
        self.inb_menu1 = tk.Menubutton( self.mainframe , width = 16 ,text = 'インブリード(英語名', relief=tk.RIDGE , bg = 'plum1')
        self.inb_menu1.grid( row = 3 , column = 4 )
        self.inb_menu1.menu = tk.Menu(self.inb_menu1 , tearoff = 0)
        #メニュー項目のセット
        self.inb_menu1.menu.add_separator()#区切りと、インブリードリストのチェックをクリアするメソッド呼び出し
        self.inb_menu1.menu.add_command( label = 'チェックをクリア' , command = self.c_mark_clear(1))
        self.inb_menu1.menu.add_separator()
        for i in range( 0 , len (self.dic_key1)):
            self.inb_menu1.menu.add_checkbutton( label = self.dic_key1[i] , onvalue = True ,
                            offvalue = False , variable = self.inb_chk1[i] )
        self.inb_menu1['menu'] = self.inb_menu1.menu
        self.inb_menu1.menu.add_separator()#区切りと、インブリードリストのチェックをクリアするメソッド呼び出し
        self.inb_menu1.menu.add_command( label = 'チェックをクリア' , command = self.c_mark_clear(2))

        #インブリード検索2
        self.inb_menu2 = tk.Menubutton( self.mainframe , width = 16 ,text = 'インブリード(日本語名', relief=tk.RIDGE , bg = 'plum2')
        self.inb_menu2.grid( row = 3 , column = 5 )
        self.inb_menu2.menu = tk.Menu(self.inb_menu2 , tearoff = 0)
        #メニュー項目のセット
        self.inb_menu2.menu.add_separator()#区切りと、インブリードリストのチェックをクリアするメソッド呼び出し
        self.inb_menu2.menu.add_command( label = 'チェックをクリア' , command = self.c_mark_clear(2))
        self.inb_menu2.menu.add_separator()
        for i in range( 0 , len (self.dic_key2)):
            self.inb_menu2.menu.add_checkbutton( label = self.dic_key2[i] , onvalue = True ,
                            offvalue = False , variable = self.inb_chk2[i] )
        self.inb_menu2['menu'] = self.inb_menu2.menu
        self.inb_menu2.menu.add_separator()#区切りと、インブリードリストのチェックをクリアするメソッド呼び出し
        self.inb_menu2.menu.add_command( label = 'チェックをクリア' , command = self.c_mark_clear(2))


        #情報ウィンドウ
        self.mw01 = ScrolledText( self.mainframe , height = 12, width = 80 ,
                                  padx = 15 , pady = 15 , relief = 'groove')
        self.mw01.grid( row = 6, column = 0 , columnspan = 6)
        



    #選択リストのインブリードに付いたチェックマークを一括クリア
    #引数1...英語名のリスト 2...日本語名のリスト
    def  c_mark_clear(self , num ):
        def t():
            if num == 1:
                for i in range( 0 , len( self.inb_chk1 ) ):
                    self.inb_chk1[i].set(False)
            else:
                for i in range( 0 , len( self.inb_chk2 ) ):
                    self.inb_chk2[i].set(False)
        return t
        

        

    #引数のタプルは、何列目の何個目のチェックをへんこうするのかの動作確認用
    def set_blood(self,tpl):
        def t():
            print(tpl)
            for i in range(0,15):
                print('check',self.omo[tpl[0]][i].get() )
        return t

        
    #引数 flg s->牡馬 b->牝馬　の検索を実行
    #面白配合のチェックをしている列の系統に該当する馬を検索する。
    #どこにもチェックが入っていない列は、すべてが検索対象になる
    def search_start(self,flg):
        def t():
            txt = ''
            #表示確認用文字列
            omotxt = ['面白1(父)に...','面白2(父母父)に...','面白3(母父)に...','面白4(母母父)に ...']
            tmphorse = []
            #del tmphorse[:]
            chk_all = 0#全部のチェックがついていないラインの場合は0のまま
            allselected = 0
            tmpbld = []
            tmpinb = []
            for i in range(0,4):
                txt += omotxt[i]#表示確認用テキスト
                for j in range(0,15):
                    if self.omo[i][j].get() == True:
                        chk_all = 1
                        tmpbld.append( self.bld_txt[j] )#検索対象となる系統名をリストに入れる
                        txt += self.bld_txt[j]#表示確認用テキスト

                if chk_all == 0:#いずれもTrueではないラインだった
                    #それ用の処理めそっどのフラグ
                    allselected = 1
                    txt += 'いずれか'#表示確認用テキスト
                if flg == 's':#牡馬の場合
                    for s in ds.stallions:
                        s.check_omo_blood( i , tmpbld , allselected )
                elif flg == 'b':#牝馬の場合
                    for b in ds.broodmares:
                        b.check_omo_blood( i , tmpbld , allselected )
                txt += '\n'

                    
                del tmpbld[:]
                chk_all = 0#フラグクリア
                allselected = 0

            #インブリード検索リスト作成とサーチ
            for c in range( 0 , len(self.inb_chk1) ):#英語インブリード名を検索対象に追加
                if self.inb_chk1[c].get() == True:
                    tmpinb.append( self.dic_key1[c] )
            for c in range( 0 , len(self.inb_chk2) ):#日本語インブリード名を検索対象に追加
                if self.inb_chk2[c].get() == True:
                    tmpinb.append( self.dic_key2[c] )
            if len(tmpinb) == 0:#インブリード検索対象がない場合全通しflgオン
                allselected = 1
                txt += '(インブリードは問わず)\n'
            else:
                txt += 'インブリードに'
                for i in tmpinb:
                    txt += '{} '.format(i)
                txt += 'を持つ馬\n\n'
            #検索
            if flg == 's':#牡馬の場合
                for s in ds.stallions:
                    s.check_inb( tmpinb , allselected )
            elif flg == 'b':#牝馬の場合
                for b in ds.broodmares:
                    b.check_inb( tmpinb , allselected )

            #対象馬抽出
            if flg == 's':
                for s in ds.stallions:
                    if s.selected[0]==1 and s.selected[1]==1 and  s.selected[2]==1 and s.selected[3]==1 and s.hav_inb == 1:
                        tmphorse.append(s)
            elif flg == 'b':
                for b in ds.broodmares:
                    if b.selected[0]==1 and b.selected[1]==1 and  b.selected[2]==1 and b.selected[3]==1 and b.hav_inb == 1:
                        tmphorse.append(b)

            #結果表示
            if len( tmphorse ) != 0:
                txt += '検索にヒットした馬は...\n'
                for h in tmphorse:
                    txt += '{0} {1:<25} {2[0]}-{2[1]}-{2[2]}-{2[3]}\n'.format( h.rare , h.name , h.omoshiro )
                txt += 'になります'
            else:
                txt += '\n\n\n検索にヒットした馬はいませんでした\n'
            self.show_message01(txt , 1)
        return t


    #情報表示ウィンドウにメッセージを表示
    #引数txt..　テキスト　flg=0...追加表示 flg=1...消去して表示
    def show_message01(self, txt , flg = 1 ):
        if flg == 1:#テキストウィンドウを消去
            self.mw01.delete( 1.0 , tk.END )
        self.mw01.insert( tk.END , txt )




#馬データ
class horse:
    def __init__(self , data ):
        self.name = ''
        self.rare = 0
        self.omoshiro = ['','','','']
        self.migoto = ['','','','']
        self.blood = ['','','','','','','','','','','','','','','']#インブリード用馬名
        self.pedigree = ['','','','','','','','','','','','','','','']#系統名
        self.set_data(data)
        self.selected = [0,0,0,0]#検索対象フラグ 1なら検索対象に
        self.hav_inb = 0#検索対象のインブリードを持っているか


    #インスタンス時のデータ初期化
    def set_data( self , data):
        self.name = data[0]
        self.rare = int( data[1] )
        for i in range(0,15):
            self.blood[i] = data[ i + 2 ]
        for i in range(0,15):
            self.pedigree[i] = data[i + 17]
        self.set_omoshiro()
        self.set_migoto()
    

    #検索用の面白配合の系統をセット
    def set_omoshiro(self):
        self.omoshiro[0] = ds.hblood[ self.pedigree[0] ]
        self.omoshiro[1] = ds.hblood[ self.pedigree[5] ]
        self.omoshiro[2] = ds.hblood[ self.pedigree[8] ]
        self.omoshiro[3] = ds.hblood[ self.pedigree[12] ]


    #検索条件用の見事配合の系統をセット
    def set_migoto(self):
        self.migoto[0] = ds.hblood[ self.pedigree[4] ]
        self.migoto[1] = ds.hblood[ self.pedigree[7] ]
        self.migoto[2] = ds.hblood[ self.pedigree[11] ]
        self.migoto[3] = ds.hblood[ self.pedigree[14] ]


    #自分の確認表示用のテキストを返す。その詳細版
    #返り値は表示用のテキスト
    def show_selfdata(self):
        txt = 'Rare:{} {}\n\n'.format( self.rare , self.name )
        txt += '面白配合用系統  {0[0]} {0[1]} {0[2]} {0[3]}\n'.format( self.omoshiro )
        txt += '見事配合用系統  {0[0]} {0[1]} {0[2]} {0[3]}\n\n'.format( self.migoto )
        txt += 'インブリード血統\n\n'
        for i in range(0,15):
            txt += '{} {}    {}\n'.format( ds.fmnew[i] , self.blood[i] , ds.get_inbreed( self.blood[i] ) )
        txt += '\n\n系統\n\n'
        for i in range(0,15):
            txt += '{} {}\n'.format( ds.fmnew[i] , self.pedigree[i] )
        return txt

    #自分のデータ確認表示用、その項目を絞ったもの
    #返り値は表示用のテキスト
    def show_selfdata_light(self):
        txt = 'Rare:{} {}\n\n'.format( self.rare , self.name )
        txt += '面白配合用系統  {0[0]} {0[1]} {0[2]} {0[3]}\n\n'.format( self.omoshiro )
        txt += '見事配合用系統  {0[0]} {0[1]} {0[2]} {0[3]}\n\n\n'.format( self.migoto )
        txt += 'インブリード血統\n\n'
        for i in range(0,15):
            tmp = ds.get_inbreed( self.blood[i] )
            if tmp != '':
                txt += '{} に {}    {} のインブリードあり\n'.format( ds.fmnew[i] , self.blood[i] ,tmp)

        return txt



    #外部から呼ばれる、検索対象フラグをセットするメソッド
    #引数 bldlst...検索対象系統の名前が入ったリスト line...何列目か flg...1の場合、全通し
    def check_omo_blood(self , line , bldlst , flg = 0 ):
        if flg == 1:
            self.selected[line] = 1
        else:
            if self.omoshiro[line] in bldlst:#検索対象に合致しているか
                self.selected[line] = 1
            else:
                self.selected[line] = 0


    #外部から呼ばれる、検索対象フラグをセットするメソッド
    #引数 bldlst...検索対象インブリード名が入ったリスト flg...1の場合、全通し
    def check_inb(self , inblst , flg = 0 ):
        inbchk = 0
        if flg == 1:
            inbchk = 1
        else:
            for b in self.blood:
                if b in inblst:
                    inbchk = 1
        
        if inbchk == 1:
            self.hav_inb = 1
        else:
            self.hav_inb = 0


    #簡易テキスト表示用に、対象馬との有効インブリードがあれば、それだけを表示するためのテキストを返す
    #引数はチェック対象の馬のクラスデータ
    def check_inbreed_light(self , horse ):
        tmp = ''#インブリードの効果があるかどうかの返り値受け
        rettxt = ''
        for i in self.blood:#自分のインブリード血統でイテレート
            tmp = ds.get_inbreed( i )#血統名を渡して、インブリード効果があるのならその効果名が返ってくる
            #馬と血統がクロスしていれば効果を記載
            if tmp != '':#チェック中の血統が効果があるインブリードを持っているのなら
                if i in horse.blood:#なおかつ対象馬のインブリードとクロスしているのか
                    rettxt += '{}  _{}のインブリードあり\n'.format( i , tmp)
            tmp = ''

        return rettxt


    #よくできた配合になる対象馬のリスト番号をリスト返す
    #引数flg ...'s'自身が牡馬　'b'自身が牝馬 horseはクラスのリストで、検索対象が牡馬か牝馬かどちらか
    def goodsearch(self , flg , horse ):
        retlist = []
        if flg == 's':#自身が牡馬の場合
            for i,h in enumerate( horse ):
                if ds.search_good( h.omoshiro , self.migoto ):#牝馬の面白リスト、牡馬の見事リストを渡すとフラグが返ってくる
                    retlist.append(i)
        elif flg == 'b':#自身が牝馬の場合
            for i,h in enumerate( horse ):
                if ds.search_good( self.omoshiro , h.migoto ):#牝馬の面白リスト、牡馬の見事リストを渡すとフラグが返ってくる
                    retlist.append(i)

        return retlist



        
    #面白配合になる対象馬のリスト番号をリスト返す
    #引数flg ...'s'自身が牡馬　'b'自身が牝馬 horseはクラスのリストで、検索対象が牡馬か牝馬かどちらか
    #flgは使わないが、形式併せるために残しとく
    def funnysearch(self , flg , horse ):
        retlist = []
        
        for i,h in enumerate( horse ):
            if ds.search_funny( h.omoshiro + self.omoshiro ):#牝馬の面白リスト、牡馬の見事リストを渡すとフラグが返ってくる
                retlist.append(i)
        return retlist


    #(自分が牡馬の時)引数クラスの牝馬との子供のクラスを渡す
    #返り値は新しくできる子供の馬クラス
    def make_horse_to_broodmare(self , b_horse ):
        tmpdat = []#子供データを作成する配列
        
        s_namelen = 4#名前決定時に短すぎる時のためにスライス幅を取らないといけないな…
        b_namelen = 4#
        if len(self.name) < 4:
            s_namelen = len(self.name)
        if len(b_horse.name) < 4:
            b_namelen = len(b_horse.name)

        tmpdat.append( self.name[: s_namelen ] + ' x ' + b_horse.name[:b_namelen ] )#名前
        tmpdat.append( self.rare )#レア度
        #インブリード血統名
        #まず自分の名前
        #追加処理、年号馬の年号を抜く処理
        chk = re.search(r'[0-9]{4}',self.name)
        if chk != None:#年号を発見した場合
            delstr = self.name[ chk.span(0)[0] : chk.span(0)[1] ]#年号抽出
            output = self.name.replace(delstr,'')#空白に置き換え
            tmpdat.append(output)
        else:#年号がない場合はそのまま
            tmpdat.append(self.name)

        addlist_self = [0,1,2,5,8,9,12]#次世代に引き継ぐ血のリスト番号
        for i in addlist_self:
            tmpdat.append( self.blood[i] )
        for i in addlist_self:
            tmpdat.append( b_horse.blood[i] )#時代に引き継ぐ血のリスト番号牝馬の分
        
        #系統名
        tmpdat.append( self.pedigree[0] )#自身の系統は父の物を引き継ぐ
        for i in addlist_self:
            tmpdat.append( self.pedigree[i] )
        for i in addlist_self:
            tmpdat.append( b_horse.pedigree[i] )#時代に引き継ぐ血のリスト番号牝馬の分   
        #print('tmpdat',tmpdat)#確認用

        child = horse(tmpdat)
        return child
        


    #牝馬のデータクラスを参照して、見事完璧になるかどうか調べ、リストのインデックス番号を返す
    #引数 's'or'b'は、自分の牡牝フラグ    h_list は馬データクラスのリスト
    def search_cross_to( self , flg , h_list ):
        ret_migotolist = []
        ret_kanpekilist = []
        omo_flg = 0
        migoto_flg = 0
        for i , h in enumerate(h_list):
            if flg == 's':#自身が牡馬の場合
                migoto_flg = ds.search_great( self.migoto , h.omoshiro )
            else:#自身が牝馬の場合
                migoto_flg = ds.search_great( h.migoto , self.omoshiro )
                
            if migoto_flg == True:#見事な配合成立の場合、完璧かどうかの判定を行う
                omo_flg = ds.search_funny( self.omoshiro + h.omoshiro )
                if omo_flg == True:#両方のフラグが立っていれば完璧
                    ret_kanpekilist.append(i)
                else:
                    ret_migotolist.append(i)

        return ret_migotolist,ret_kanpekilist







if __name__ == '__main__':
    if len(sys.argv) > 1:
        ds.DB_FILE = sys.argv[1]#スクリプト起動時にdb読み込みファイル名を指定可能に

    f = topframe()
    f.mainframe.title('derby browser')
    f.mainframe.geometry(ds.WINDOWSIZE)#変更したい場合はdsconfig.pyを変更
    f.mainframe.mainloop()

