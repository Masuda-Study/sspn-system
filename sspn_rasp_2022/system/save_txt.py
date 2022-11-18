#
#
# .txtで測位結果を保存するためのプログラム
#
# 保存する形式は
# 
# [time:〇〇,1ch:〇〇,2ch:〇〇,3ch:〇〇,4ch:〇〇] 
# [point-x:〇〇,point-y:〇〇,point-z:〇〇]
#               ↓
# [1ch,2ch,3ch,4ch=〇〇,〇〇,〇〇,〇〇]
# [x,y,z=〇〇,〇〇,〇〇]
#
#


def save_data(data,file):
    return 0




def write_text(distance, correct):
    
    try:
        #計測距離と補正値を1つの変数に格納
        text = "計測距離:" + str(distance) + "\n補正値:" + str(correct) + '\n'

        #書き込むデータをターミナルに表示
        print(text)
        
        #textファイルを開いて書き込む(aモード)
        f = open('./textfile/test.txt', 'a')
        f.writelines(text)
        f.close()
        
    except Exception as e:
        print("dont write txt:\n")
        print(e)