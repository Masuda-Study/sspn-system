import json #jsonの形式を扱う


def get_json(json_file_name):
    json_file = open(json_file_name,'r',encoding="utf-8_sig")
    json_data = json.load(json_file)
    del json_data['_comments'] #JSONのコメント行を削除
    #print(json_data['name'])
    return json_data
