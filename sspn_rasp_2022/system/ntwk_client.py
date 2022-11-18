import socket
import time
import datetime
import pickle

HOST_IP = "172.16.147.194" # 接続するサーバーのIPアドレス
PORT = 12345 # 接続するサーバーのポート
DATESIZE = 1024 # 受信データバイト数
INTERVAL = 1 # ソケット接続時のリトライ待ち時間
RETRYTIMES = 100 # ソケット接続時のリトライ回数

SP_MIC_DISTANCE = [0,0,0,0]
POINT = []

"""
def main():
    #1 オープン
    client = SocketClient(HOST_IP, PORT)
    client.connect() # はじめの1回だけソケットをオープン
    
    while True:
        #2 測位結果をほかのとこから持ってくる(ここはそういう関数を作る)
        SP_MIC_DISTANCE = [1600,1600,1600,1600]
        #3送る
        if client.socket is not None:
             # quitが戻ってくる(自分でquitと入力する)とソケットをクローズして終了
            #if client.send_dist_loop() == 'quit':
            #    client.close()
            data = client.send_dist_loop(SP_MIC_DISTANCE)
            print(data)
        else:
            break
        time.sleep(1)
"""

class SocketClient():

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
    
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       
    
        # サーバーとの接続 RETRYTIMESの回数だけリトライ
        for x in range(RETRYTIMES):
            try:
                client_socket.connect((self.host, self.port))
                self.socket =  client_socket
                print('[{0}] server connect -> address : {1}:{2}'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), self.host, self.port) )
                break
            except socket.error:
                # 接続を確立できない場合、INTERVAL秒待ってリトライ
                time.sleep(INTERVAL)
                print('[{0}] retry after wait{1}s'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), str(INTERVAL)) )
 
    # サーバーへデータ送信関数


    def send_dist(self,arr):
        data = pickle.dumps(arr)
        self.socket.send(data)
        return self.recv()
    
    # サーバーからデータ受信関数
    def recv(self):
        rcv_data = self.socket.recv(DATESIZE) # データ受信
        rcv_data = rcv_data.decode('utf-8')
        return rcv_data
    
    #
    # 上記の送信/受信関数を順番に行う
    # ここの関数を下のメインの部分で動かしている

    
    def send_dist_to_server(self,dist_arr):
        self.send_dist_loop(dist_arr)
        return self.recv()

    # ソケットをクローズする関数
    def close(self):
        self.socket.close() # ソケットクローズ
        self.socket = None
             