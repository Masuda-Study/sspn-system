########################
##
##このプログラムは受信側増幅基板につながっているマイコンとかラズパイ用
##基本的には値を取ってきて距離計算、座標計算をしてからサーバに送信するためのプログラム
##あとあとmac addressとか個体固有の物が必要になると思うのでとりあえず共通部分のみ作る
##
###########################




#モジュール等呼び出し
import FPGA_serial #FPGAとシリアル通信をしてデータを取り出すモジュール
import positioning_ultrasound #測位計算と誤差計算をするためのモジュール
import json_info #json情報を持ってきて、利用するモジュール
import save_txt #テキストで保存するための関数
#ライブラリのインポート
from queue import Queue #スレッド間通信のためのキュー
import threading 
import datetime #現在時刻の取得用
import os
#network
import socket
import pickle
from ntwk_client import *
from get_temperature import *
from bme280 import *


#csv操作
import csv
import pprint
#sleep用
import time
import smbus
#i2C用
#import smbus
#import sys

#絶対パスのほうがいいかもだけど相対パスの方がいろいろ使いやすいかも～
json_file_name = "./setting.json"
txt_file_name = "./textfile/test.txt"


#############################################
#
#変数等定義部
#
###########################################

HOST_IP = "172.16.147.194" # 接続するサーバーのIPアドレス
PORT = 12345 # 接続するサーバーのポート
DATESIZE = 1024 # 受信データバイト数
INTERVAL = 2 # ソケット接続時のリトライ待ち時間
RETRYTIMES = 10 # ソケット接続時のリトライ回数

#setting.jsonの内容が入っている
# ポート情報
setting_info =""
port_name = ["LPS_ser","Arduino_ser"]

#キューをグローバル化->必要か微妙
point_queue = ""
dist_queue = ""
backup_queue = ""

#azureへ送信するJSON形式のフォーマット
#MSG_TXT = '{{"timeID":{timeID},"timestamp": "{timestamp}","kiki_num": {kiki_num},"x":{x},"y":{y},"z":{z}}}'
#テキストで保存するデータ
positioning_result = []

i2c_sample = 0
room_temp = 0
#スレッドを止めるための変数
#一時停止
thread_stoper = False
test_counter = 0
#完全終了
#thread_stopper_kai = False
timearr = []



######################################################################
#
#メインメソッド
#ポートやファイルの設定をしたあとにスレッドを動かす
#
#######################################################################


def main():
    global point_queue,setting_info,backup_queue,dist_queue
    global thread_stoper,thread_stopper_kai
    global client
    print("start")

    #スタートしたらまず無線通信を確立すru
    client = SocketClient(HOST_IP,PORT)
    client.connect()
    print("connection success")

    setting_info = json_info.get_json(json_file_name)
    print(setting_info)

    #最初にまず温度を取る
    #i2c_sample = 340

    #スレッド間通信用のキュー
    point_queue = Queue()
    dist_queue = Queue()
    backup_queue = Queue()

    thread_stoper = True

    #
    #
    # i2cの温度の部分に関しては今後変更予定
    # azureの部分はまだ実装する予定なし
    #
    thread_sokui = threading.Thread(target=sokui_thread, args=(setting_info["LPSEpsilon"],))
    thread_ntwk  = threading.Thread(target=send_server_thread)

    thread_sokui.start()
    thread_ntwk.start()

    thread_sokui.join()
    thread_ntwk.join()

    print("end")











##################################################################################################
#測位を行い、測位計算を行うメソッド
#(空いたシリアルポート)→キューにデータ挿入
##################################################################################################

def sokui_thread(ser_info):
    global point_queue,dist_queue
    global backup_queue
    global distance,setting_info
    global port_name
    global thread_stoper#,thread_stopper_kai
    i2c = smbus.SMBus(1)
    
    #キューに保存するデータのフォーム
    #わざわざ辞書型にして保持しておく理由がないから後で変えておく、普通に配列にして対応する部分のデータをsavetxt.pyで加工して保存する
    data_form_arr = [0] * 4
    #スピーカーからマイクの距離[1ch, 2ch, 3ch, 4ch]
    sp_to_mic_tof = [0] * 4
    sp_to_mic_distance = [0] * 4
    #測位した時間と座標[time, x, y, z]
    only_point = [0] * 3 #一回こっちに入れてから下の変数に入れる
    point_and_time = [0] * 4
    print("sokui_thread_start_point")
    while True:
        if thread_stoper:
            #音速を持ってくる
            print("positioning start")
            #onsoku_sample = Arduino_tem.onsoku_keisan(ser_info[port_name[1]])
            try:
                # get temperature from sht31
                #room_temp = get_temp_byte(i2c)
                #get temperature from bme280
                setup(i2c)
                get_calib_param(i2c)
                room_temp = readData(i2c)
                print(room_temp)

                sp_to_mic_tof = FPGA_serial.start(ser_info,1)
                point_and_time[0] = positioning_time()
                
                #音速と各サンプル数をかけて距離にする
                for i in range(len(sp_to_mic_tof)):
                    sp_to_mic_distance[i] = round(calc_sp_to_mic_distance(sp_to_mic_tof[i],room_temp),3)

                print("this is distance : ",sp_to_mic_distance)
                #ゼロだと動くのがいまいちわからんのでとりあえずテストデータを入れて動かしてみる
                #一つずつ0をふやしたけど大丈夫
                #dummy data
                """
                sp_to_mic_distance[0] = 2300
                sp_to_mic_distance[1] = 2300
                sp_to_mic_distance[2] = 2300
                sp_to_mic_distance[3] = 2300
                """
                

                ########################################################################################################
                ####
                #### 測位計算
                #### pythonのみに変更完了!-> may be have some errors
                ####
                ########################################################################################################
                
                only_point = positioning_ultrasound.calc_point(sp_to_mic_distance)

                #####################################################################
                #　一応配列にして入れてあるこれをキューに入れて保存するようにする
                data_form_arr[0] = point_and_time[0]
                data_form_arr[1] = round(only_point[0],2)
                data_form_arr[2] = round(only_point[1],2)
                data_form_arr[3] = round(only_point[2],2)
                print("data_form_arr",data_form_arr)

                #距離もとって置きたいからキューに入れておく
                #それぞれをキューに入力
                point_queue.put(data_form_arr)
                dist_queue.put(sp_to_mic_distance)
                
                #1秒ちょっとで一回測位するためー＞なんかスリープ関数だと処理全体が止まってしまうらしいから他の処理を邪魔しないタイプのWAITがあればそういうのを使いたい
                time.sleep(1)
                
            except Exception as e:
                print(e)
                print("POSITIONING THREAD ERROR!")
        else :
            time.sleep(0.5)


def send_server_thread():
    global thread_stoper
    global point_queue,dist_queue
    global client
    loop_count = 0


    test_arr = [-1,-1,-1,-1,-1]
    send_point_data = [2,0,0,0,0]
    send_dist_data = [1,0,0,0,0]

    while True:
        if thread_stoper:
            print("communicate with server !!")
            print("size",point_queue.qsize())
            if point_queue.qsize()>0:
                # judge what data is
                send_dist_data_temp = dist_queue.get()
                #send_dist_data.insert(0,1)
                for i in range(4):
                    send_dist_data[i+1] = send_dist_data_temp[i]
                send_dist_data[0] = 1
                data = client.send_dist(send_dist_data)
                print(send_dist_data)

                send_point_data_temp = point_queue.get()
                #send_point_data.insert(0,2)
                for i in range(4):
                    send_point_data[i+1] = send_point_data_temp[i]
                send_dist_data[0] = 2
                data = client.send_dist(send_point_data)
                print(send_point_data)

                """
                if loop_count > 0:
                    del send_dist_data[-1]
                    del send_point_data[-1]
                loop_count += 1
                """
            else:
                send_point_data = test_arr
                send_dist_data = test_arr        
            time.sleep(1)

            
            """
            if client.socket is not None:
                if client.send_dist(test_arr) == 'quit':
                    client.close()
                data = client.send_dist(test_arr)
                print(data)
                time.sleep(1)
            else:
                break
            """




##################################################################################################
#
#csvとしてデータをバックアップするメソッド
#TXT変更する
##################################################################################################

def save_positioning_data_thread(file):
    global backup_queue
    global thread_stoper#,thread_stopper_kai
    #while thread_stopper_kai:
        #while thread_stoper:
    while True:
        if thread_stoper:
            data = backup_queue.get()
            #print(data)
            save_txt.save_data(data,file)
            time.sleep(0.03)
        else: 
            time.sleep(0.01)

##################################################################################################
#
#TOFから距離を計算するメソッド、ついでに1サンプルに対しての距離も同時に計算してある
#
##################################################################################################

def calc_sp_to_mic_distance(tof,room_temp):
    sound_speed = 331.5 + (0.6 * room_temp)
    distance_per_sample = (sound_speed * 0.001) * 6.25
    return tof * distance_per_sample



##################################################################################################
#現在の時刻を取得して西暦の下2桁、月日時間で作ったIDを戻す　(例:20122919340618)
#→TimeID
#とりあえずそこまで詳細な日時(マイクロ秒とか)はいらないから(年月日時分秒=20220427165905)
#timeID gene() -> positioningtimeに変更 
##################################################################################################

def timeID_gene():
    now = datetime.datetime.now()
    timeID = str(now.year)[2:4]+str(now.month)+str(now.day).zfill(2)+str(now.hour).zfill(2)+str(now.minute).zfill(2)+str(now.second).zfill(2)+str(now.microsecond).zfill(6)[0:2]
    return timeID

def positioning_time():
    timearr = [0]*7
    current_time = datetime.datetime.now()
    timearr[0] = str(current_time.year)
    #10より小さかったら前に0を入れる→単純に桁がそろうから使いやすいかなっていう配慮
    if current_time.month<10:
        timearr[1] = "0" + str(current_time.month)
    else:
        timearr[1] = str(current_time.month)

    if current_time.day<10:
        timearr[2] = "0" + str(current_time.day)
    else:
        timearr[2] = str(current_time.day)

    if current_time.hour<10:
        timearr[3] = "0" + str(current_time.hour)
    else:
        timearr[3] = str(current_time.hour)

    if current_time.minute<10:
        timearr[4] = "0" + str(current_time.minute)
    else:
        timearr[4] = str(current_time.minute)

    if current_time.minute<10:
        timearr[5] = "0" + str(current_time.minute)
    else:
        timearr[5] = str(current_time.minute)

    if current_time.second<10:
        timearr[6] = "0" + str(current_time.second)
    else:
        timearr[6] = str(current_time.second)

    return str(timearr[0] + timearr[1] + timearr[2] + timearr[3] + timearr[4] + timearr[5] + timearr[6])


##################################################################################################
#
#　メインスタート
#
##################################################################################################  
if __name__ == "__main__":
    main()