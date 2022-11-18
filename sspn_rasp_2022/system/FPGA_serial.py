
import serial  #pythonでシリアル通信をするためのパッケージを持ってくる
from time import sleep   #一時停止の時に使うパッケージ
import codecs

#イプシロンと通信をするポート(他のモジュールでやるため不要)
#LPSEpsilon = '/dev/ttyUSB0'

#読み込みデータを保存する配列(測位回数を変える場合注意)-----
readdate =[[]] #[]の分だけデータが取れ
read_data_from_fpga = [[]]
#------------------------------------------------------

count=1  #測位した回数のカウンタ

#コマンドデータ---------------------------------------
senddata = 255 #0xff
senddata2 = 82 #0x52=Ascii:R
senddata3 = 8  #0x0 = 参照レジスタ番地
senddata4 = 0  #0x0 = ごみ(読み込みの時は使用しない場所)
#------------------------------------------------------

#それぞれのチャンネルのサンプル数を保存しておく配列--------------------
distance_sample = {"tm_ctr0":[0],"tm_ctr1":[0],"tm_ctr2":[0],"tm_ctr3":[0]}
#辞書型は使いにくいから配列に変更する,[1ch, 2ch, 3ch, 4ch]--ちなここでとれるのは距離ではない
sp_to_mic_tof = [0,0,0,0]
#-------------------------------------------------------------------

#チャンネルにあったTOFの辞書の名前-------------------
ch_name = ["tm_ctr0","tm_ctr1","tm_ctr2","tm_ctr3"]
#---------------------------------------------------

stop_time = 0.00001 #停止時間




#############################################################################################
#測距情報を取り出す処理をスタートさせるもの
# i は取り出すレジスタの番号(8-15)
# serはシリアルポート
# countaは測距データを取り出す回数
##############################################################################################
def start(ser_info,positioning_times):
    global count,senddata3,read_data_from_fpga,sp_to_mic_tof
    #print("測距スタート")
    count = 1
    ser = serial.Serial(ser_info,9600,timeout=0.5) 
    read_data_from_fpga  = [[] for z in range(positioning_times)]
    #distance_sample = {"tm_ctr0":[],"tm_ctr1":[],"tm_ctr2":[],"tm_ctr3":[]}
    sp_to_mic_distance = [0,0,0,0]
    while count <= positioning_times:
        i = 8   #レジスタの8未満は今は使用しない、８番以上のレジスタに測距情報が入っている
        #レジスタの値を取り出す------------------------------------------
        while i < 16:
            senddata3 = int(i)  #ここで取り出すレジスタの番地を代入(8~16番を指定している)
            get_data_from_FPGA(ser,count-1,'big')#,9600,'big') #fpgaにコマンド送信→測距データを取得
            i += 1
        #--------------------------------------------------------------
        Join(count-1)
        #ここで取得したバイト列を表示している
        #print("read data from fpga ",read_data_from_fpga)
        sleep(stop_time)
        #sleep(1.022)  #FT232Hの使用上処理をストップさせる(こんなに必要かは微妙)
        count+=1
        
    ser.close()
    #print("多分fpgaとかの最後の部分",sp_to_mic_tof)
    return sp_to_mic_tof



##############################################################################################
#ser = serial.Serial(LPSEpsilon,rate,timeout=None)  #USBシリアル通信をするポートとボーレート、タイムアウトをする時間を設定する
#コマンドを送信して、レジスタの値を取り出す(読み出し回数,ボーレート,エンディアン)-----
##############################################################################################

def get_data_from_FPGA(ser,rcount,end):#,rate,end):
    global read_data_from_fpga
    ser.write(senddata.to_bytes(1,end))  #データを書き込む
    sleep(stop_time)  #0.001秒停止(ステートマシンを動き終わるまで待つ)(nsの世界だから/100をしてみる)
    ser.write(senddata2.to_bytes(1,end))
    sleep(stop_time)
    ser.write(senddata3.to_bytes(1,end))
    sleep(stop_time)
    ser.write(senddata4.to_bytes(1,end))
    sleep(stop_time)
    ser.write(senddata4.to_bytes(1,end))
    sleep(stop_time)
    ser.write(senddata4.to_bytes(1,end))
    sleep(0.0001)

    line = ser.read(1)  #データを取得
    read_data_from_fpga[rcount].append(line)  #読み込み配列にデータを入力する
    

#---------------------------------------------------------------------------


##############################################################################################
#サンプル数を配列に入力(取得したサンプル数を処理するプログラムを呼び出す)---------------------------
#rnumberはレジスタのカウント数
def Join(rcount):
    rnumber = 0
    #3/24:リセットをかけてデータがなかった場合でもエラーが出ないようにする
    try:
        while(rnumber<4):
            sample_Join(rcount,rnumber) 
            rnumber+=1
    except Exception as e:
        print(e)
        print("dont work sample join ! \n")
#--------------------------------------------------------------



##############################################################################################
#サンプルを保存する配列に振り分ける(取り込んだバイト列を16ビットに組み合わせて、int型に変更して配列に振り分けている)------------------
def sample_Join(rcount,number):
    #global distance_sample
    global read_data_from_fpga,sp_to_mic_tof
    #ここ結構怪しい動作してるから要確認
    sp_to_mic_tof[number] = int(codecs.encode(read_data_from_fpga[rcount][number*2+1] + read_data_from_fpga[rcount][number*2], 'hex'),16)
    
#----------------------------------------------------------------------------------------------------------------------------


