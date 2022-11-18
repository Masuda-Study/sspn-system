
#
#
# 目的
#
# 現在超音波の各距離を測位し座標計算においてすべてC言語のプログラムによって行われている
# そして岡田さんはそれをCythonとかいうくそだるい技術によってlinux限定の○○プログラムと化している
# 何とか訂正しなければならないためこの距離計算の部分をモジュール化する
#
#


#ライブラリ
import math
import numpy


#変数宣言

#スピーカーの座標 [x,y,z]
"""
spk_1ch = [500,2000,0]
spk_2ch = [1000,1500,0]
spk_3ch = [1500,2000,0]
spk_4ch = [1000,2500,0]
"""

#スピーカーを上に配置した時の座標(コミュニケーションロボット用)

spk_1ch = [0,0,3000]
spk_2ch = [3000,0,3000]
spk_3ch = [3000,3000,3000]
spk_4ch = [0,3000,3000]

#計算した結果→座標
point_x = 0
point_y = 0
point_z = 0

#計算対象→それぞれのチャンネルから受信機までの距離
len_1ch = 0
len_2ch = 0
len_3ch = 0
len_4ch = 0

#何回測位したか
check = [0]
#測位結果
pn_ = [0] * 3
pn_result = [0] * 3

x = [[0]*4]
y = [[0]*4]
z = [[0]*4]


"""
def main():
    ch1 = int(input("ch1:"))
    ch2 = int(input("ch2:"))
    ch3 = int(input("ch3:"))
    ch4 = int(input("ch4:"))

    calc_point(ch1,ch2,ch3,ch4)

    print(pn_result)
    return 0
"""


#関数宣言

#4つの距離を入力，すると座標が帰ってくる

def calc_point(arr_r):
    i = 0

    adlen = [[0] * 3] * 4
    len_1ch = arr_r[0]
    len_2ch = arr_r[1]
    len_3ch = arr_r[2]
    len_4ch = arr_r[3]

    #まずはxyのそれぞれの辺の長さ→三角測量
    len_x12 = spk_1ch[0] - spk_2ch[0]
    len_y12 = spk_1ch[1] - spk_2ch[1]
    len_x21 = spk_2ch[0] - spk_1ch[0]
    len_y21 = spk_2ch[1] - spk_1ch[1]

    len_x13 = spk_1ch[0] - spk_3ch[0]
    len_y13 = spk_1ch[1] - spk_3ch[1]
    len_x31 = spk_3ch[0] - spk_1ch[0]
    len_y31 = spk_3ch[1] - spk_1ch[1]

    len_x14 = spk_1ch[0] - spk_4ch[0]
    len_y14 = spk_1ch[1] - spk_4ch[1]
    len_x41 = spk_4ch[0] - spk_1ch[0]
    len_y41 = spk_4ch[1] - spk_1ch[1]

    len_x23 = spk_2ch[0] - spk_3ch[0]
    len_y23 = spk_2ch[1] - spk_3ch[1]
    len_x32 = spk_3ch[0] - spk_2ch[0]
    len_y32 = spk_3ch[1] - spk_2ch[1]

    len_x24 = spk_2ch[0] - spk_4ch[0]
    len_y24 = spk_2ch[1] - spk_4ch[1]
    len_x42 = spk_4ch[0] - spk_2ch[0]
    len_y42 = spk_4ch[1] - spk_2ch[1]


    #次にそれぞれの同チャンネルの組み合わせのxyから斜辺を出して
    #多分だけど二つの点から求められる推定座標までの距離（dの辺から直角で）
    #1ch, 2chの間について
    len_d12 = math.sqrt(pow(len_x12,2) + pow(len_y12,2))
    len_l21 = (pow(len_1ch,2) - pow(len_2ch,2) + pow(len_d12,2)) / (2*len_d12)
    k21 = spk_1ch[0]*len_x21 + spk_1ch[1]*len_y21 + len_l21*len_d12
    #1ch, 3chの間について
    len_d13 = math.sqrt(pow(len_x13,2) + pow(len_y13,2))
    len_l31 = (pow(len_1ch,2) - pow(len_3ch,2) + pow(len_d13,2)) / (2*len_d13)
    k31 = spk_1ch[0]*len_x31 + spk_1ch[1]*len_y31 + len_l31*len_d13    
    #1ch, 4chの間について
    len_d14 = math.sqrt(pow(len_x14,2) + pow(len_y14,2))
    len_l41 = (pow(len_1ch,2) - pow(len_4ch,2) + pow(len_d14,2)) / (2*len_d14)
    k41 = spk_1ch[0]*len_x41 + spk_1ch[1]*len_y41 + len_l41*len_d14
    #2ch, 3ch
    len_d23 = math.sqrt(pow(len_x23,2) + pow(len_y23,2))
    len_l32 = (pow(len_2ch,2) - pow(len_3ch,2) + pow(len_d23,2)) / (2*len_d23)
    k32 = spk_2ch[0]*len_x32 + spk_2ch[1]*len_y32 + len_l32*len_d23
    #2ch, 4ch
    len_d24 = math.sqrt(pow(len_x24,2) + pow(len_y24,2))
    len_l42 = (pow(len_2ch,2) + pow(len_4ch,2) + pow(len_d24,2)) / (2*len_d24)
    k42 = spk_2ch[0]*len_x42 + spk_2ch[1]*len_y42 + len_l42*len_d24


    #ここ何の変数なのかいまいちよくわからない 
    #多分最小二乗法っていうのをやってると思う(GNSS測量で一般的なやつ)
    #どこを中心に考えるかで計算結果が4つ出てくるってことだと思う
    x_ = [[0],[0],[0],[0]]
    y_ = [[0],[0],[0],[0]]
    z_ = [[0],[0],[0],[0]]

    #それぞれのスピーカー同士の距離
    len12 = math.sqrt(pow((spk_1ch[0]-spk_2ch[0]),2) + pow((spk_1ch[1]-spk_2ch[1]),2) + pow((spk_1ch[2]-spk_2ch[2]),2)) 
    len13 = math.sqrt(pow((spk_1ch[0]-spk_3ch[0]),2) + pow((spk_1ch[1]-spk_3ch[1]),2) + pow((spk_1ch[2]-spk_3ch[2]),2))
    len14 = math.sqrt(pow((spk_1ch[0]-spk_4ch[0]),2) + pow((spk_1ch[1]-spk_4ch[1]),2) + pow((spk_1ch[2]-spk_4ch[2]),2))
    len23 = math.sqrt(pow((spk_2ch[0]-spk_3ch[0]),2) + pow((spk_2ch[1]-spk_3ch[1]),2) + pow((spk_2ch[2]-spk_3ch[2]),2))
    len24 = math.sqrt(pow((spk_2ch[0]-spk_4ch[0]),2) + pow((spk_2ch[1]-spk_4ch[1]),2) + pow((spk_2ch[2]-spk_4ch[2]),2))
    len34 = math.sqrt(pow((spk_3ch[0]-spk_4ch[0]),2) + pow((spk_3ch[1]-spk_4ch[1]),2) + pow((spk_3ch[2]-spk_4ch[2]),2))

    #測距した距離の補正と座標計算をしていると思う．ただ全部にやってるわけではなく何かを軸にしてやってる

    if len12 > (len_1ch+len_2ch): adlen[0][0] = (len12-(len_1ch+len_2ch))/2
    if len13 > (len_1ch+len_3ch): adlen[0][1] = (len13-(len_1ch+len_3ch))/2
    if len23 > (len_2ch+len_3ch): adlen[0][2] = (len23-(len_2ch+len_3ch))/2

    if adlen[0][0] < adlen[0][1]:adlen[0][0] = adlen[0][1]
    if adlen[0][0] < adlen[0][2]:adlen[0][0] = adlen[0][2]

    len_1ch += adlen[0][0]
    len_2ch += adlen[0][0]
    len_3ch += adlen[0][0]

    x_[0][0] = (k21*len_y31 - k31*len_y21) / (len_x21*len_y31 - len_x31*len_y21)
    y_[0][0] = (k21*len_x31 - k31*len_x21) / (len_x31*len_y21 - len_x21*len_y31)

    xy00 = pow(len_1ch,2)-pow((x_[0][0]-spk_1ch[0]),2) - pow((y_[0][0]-spk_1ch[1]),2)
    if xy00 < 0:
        xy00 = 0
        x_[0][0] = 0
        y_[0][0] = 0

    #下から超音波を送信する場合は「-」がつくらしい
    z_[0][0] = (spk_1ch[2] - math.sqrt(xy00))

    if x_[0][0] <= 0 or y_[0][0] <=0 or z_[0][0] <= 0:
        x_[0][0] = 0
        y_[0][0] = 0
        z_[0][0] = 0
        check[i] = check[i]+1
    
    x[i][0] = x_[0][0]
    y[i][0] = y_[0][0]
    z[i][0] = z_[0][0]

#ここまで
#2つ目の処理

    if len12 > (len_1ch+len_2ch): adlen[1][0] = (len12-(len_1ch+len_2ch))/2
    if len14 > (len_1ch+len_4ch): adlen[1][1] = (len14-(len_1ch+len_4ch))/2
    if len24 > (len_2ch+len_4ch): adlen[1][2] = (len24-(len_2ch+len_4ch))/2

    if adlen[1][0] < adlen[1][1]:adlen[1][0] = adlen[1][1]
    if adlen[1][0] < adlen[1][2]:adlen[1][0] = adlen[1][2]
    len_1ch += adlen[1][0]
    len_2ch += adlen[1][0]
    len_4ch += adlen[1][0]

    x_[1][0] = (k21*len_y41 - k41*len_y21) / (len_x21*len_y41 - len_x41*len_y21)
    y_[1][0] = (k21*len_x41 - k41*len_x21) / (len_x41*len_y21 - len_x21*len_y41)

    xy00 = pow(len_1ch,2)-pow((x_[1][0]-spk_1ch[0]),2) - pow((y_[1][0]-spk_1ch[1]),2)

    if xy00 < 0:
        xy00 = 0
        x_[1][0] = 0
        y_[1][0] = 0

    z_[1][0] = (spk_1ch[2] - math.sqrt(xy00))

    if x_[1][0] <= 0 or y_[1][0] <=0 or z_[1][0] <= 0:
        x_[1][0] = 0
        y_[1][0] = 0
        z_[1][0] = 0
        check[i] = check[i]+1
    
    x[i][1] = x_[1][0]
    y[i][1] = y_[1][0]
    z[i][1] = z_[1][0]

#ここまで
#3つ目の処理

    if len13 > (len_1ch+len_3ch): adlen[2][0] = (len13-(len_1ch+len_3ch))/2
    if len14 > (len_1ch+len_4ch): adlen[2][1] = (len14-(len_1ch+len_4ch))/2
    if len34 > (len_3ch+len_4ch): adlen[2][2] = (len34-(len_3ch+len_4ch))/2

    if adlen[2][0] < adlen[2][1]:adlen[2][0] = adlen[2][1]
    if adlen[2][0] < adlen[2][2]:adlen[2][0] = adlen[2][2]
    len_1ch += adlen[2][0]
    len_3ch += adlen[2][0]
    len_4ch += adlen[2][0]

    x_[2][0] = (k31*len_y41 - k41*len_y31) / (len_x31*len_y41 - len_x41*len_y31)
    y_[2][0] = (k31*len_x41 - k41*len_x31) / (len_x41*len_y31 - len_x31*len_y41)

    xy00 = pow(len_1ch,2)-pow((x_[2][0]-spk_1ch[0]),2) - pow((y_[2][0]-spk_1ch[1]),2)

    if xy00 < 0:
        xy00 = 0
        x_[2][0] = 0
        y_[2][0] = 0

    z_[2][0] = (spk_1ch[2] - math.sqrt(xy00))

    if x_[2][0] <= 0 or y_[2][0] <=0 or z_[2][0] <= 0:
        x_[2][0] = 0
        y_[2][0] = 0
        z_[2][0] = 0
        check[i] = check[i]+1
    
    x[i][2] = x_[2][0]
    y[i][2] = y_[2][0]
    z[i][2] = z_[2][0]

#ここまで
#4つ目の処理

    if len23 > (len_2ch+len_3ch): adlen[3][0] = (len23-(len_2ch+len_3ch))/2
    if len24 > (len_2ch+len_4ch): adlen[3][1] = (len24-(len_2ch+len_4ch))/2
    if len34 > (len_3ch+len_4ch): adlen[3][2] = (len34-(len_3ch+len_4ch))/2

    if adlen[3][0] < adlen[3][1]:adlen[3][0] = adlen[3][1]
    if adlen[3][0] < adlen[3][2]:adlen[3][0] = adlen[3][2]
    len_2ch += adlen[3][0]
    len_3ch += adlen[3][0]
    len_4ch += adlen[3][0]

    x_[3][0] = (k32*len_y42 - k42*len_y32) / (len_x32*len_y42 - len_x42*len_y32)
    y_[3][0] = (k32*len_x42 - k42*len_x32) / (len_x42*len_y32 - len_x32*len_y42)

    xy00 = pow(len_1ch,2)-pow((x_[2][0]-spk_2ch[0]),2) - pow((y_[3][0]-spk_2ch[1]),2)

    if xy00 < 0:
        xy00 = 0
        x_[3][0] = 0
        y_[3][0] = 0

    z_[3][0] = (spk_2ch[2] - math.sqrt(xy00))

    if x_[3][0] <= 0 or y_[3][0] <=0 or z_[3][0] <= 0:
        x_[3][0] = 0
        y_[3][0] = 0
        z_[3][0] = 0
        check[i] = check[i]+1
    
    x[i][3] = x_[3][0]
    y[i][3] = y_[3][0]
    z[i][3] = z_[3][0]

  

    #ここから計算結果を取り出す

    cnt = 0

    maxcount = 0
    maxdif = 999999

    sumx = 0
    sumy = 0
    sumz = 0
    
    difx = 0
    dify = 0
    difz = 0
    dif = 0
    num = 0
    calc_num = 4

    if(check[cnt] == 3):
        calc_num = 1

    for i in range(calc_num):
        sumx = x[cnt][i]
        sumy = y[cnt][i]
        sumz = z[cnt][i]

        n=0
        maxcount = 0
        count = 0
        dif = 0

        if (x[cnt][i] >= 0.0)and(y[cnt][i] >= 0.0)and(z[cnt][i] >= 0.0):
            for j in range(4):
                if(x[cnt][j] >= 0)and(y[cnt][j] >= 0)and(z[cnt][j] >= 0)and(i != j):
                    difx = -1 * (x[cnt][j] - x[cnt][i])
                    dify = -1 * (y[cnt][j] - y[cnt][i])
                    difz = -1 * (z[cnt][j] - z[cnt][i])

                    #それぞれの軸の端の距離を入れる
                    if(difx < 4000)and(dify < 4000)and(difz < 4000):
                        sumx = sumx + x[cnt][j]
                        sumy = sumy + y[cnt][j]
                        sumz = sumz + z[cnt][j]

                        dif = dif + difx + dify + difz

                        if dif != 0:
                            count += 1
                            if(len_1ch > 10000)or(len_2ch > 10000)or(len_3ch > 10000)or(len_4ch > 10000)or(calc_num==1):
                                count -= 1

                            if(count >= maxcount)and(dif < maxdif)and(dif != 0):
                                maxcount = count
                                if(num == 2) and (maxcount != 3):
                                    n = 2
                                    pn_result[0] = sumx / maxcount
                                    pn_result[1] = sumy / maxcount
                                    pn_result[2] = sumz / maxcount

                                    if pn_[2] > pn_result[2]:
                                        pn_result[0] = pn_[0]
                                        pn_result[1] = pn_[1]
                                        pn_result[2] = pn_[2]
                                    
                                if (maxcount >= num) and (n == 0 or n == 2 or maxcount == 4):
                                    pn_result[0] = sumx / maxcount
                                    pn_result[1] = sumy / maxcount
                                    pn_result[2] = sumz / maxcount
                                    #print("pn_result:",pn_result[0])
                                    num = maxcount
                                    if num == 3:
                                        m = 1
    return pn_result



"""
#これがメインスタート
if __name__ == "__main__":
    main()

"""