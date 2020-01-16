import subprocess

class CaboCha:
    def __init__(self, exe="cabocha", encoding = "utf8"):
        """
        コンストラクタ
        @ subproc: 実行してるプロセスとは違う新しいプロセスを開始する
        @ exe: Cabocha実行開始位置
        @ encoding: エンコーディングの指定
        """
        self.proc = subprocess.Popen([exe,'-f1'],shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.encoding = encoding
    
    def tree2string(self, text):
        """
        解析の実行結果を標準出力のまま受け取るメソッド
        @ text: 係り受け解析の対象となる文字列
        """
        self.proc.stdin.write(bytes(text + '\n', self.encoding))
        self.proc.stdin.flush()
        # 出力を取得
        cabocha_out = []
        while True:
            line = self.proc.stdout.readline().decode(self.encoding)
            cabocha_out.append(line)
            if line.startswith("EOS"):
                break
                
        return "".join(cabocha_out)
    
    def tree2list(self, text):
        """
        解析の結果をリスト化して返す。
        @ text: 係り受け解析の対象となる文字列
        """
        cabocha_out = self.tree2string(text)
        # 文節ごとにリストで持つ
        phrases = [line.rstrip("\r\n") for line in cabocha_out.rstrip("\r\nEOS").split("* ") if line != ""]
        result = [] # 結果
        
        # 各文節ごとに処理
        for phrase in phrases:
            phrase_data = phrase.split("\r\n")
            # かかり先などの情報
            add_data = phrase_data[0].split(" ")
            idx = int(add_data[0])
            ahead_pidx = int(add_data[1].replace("D", ""))
            main_midx = int(add_data[2].split("/")[0])
            
            # 文節内の形態素情報リスト
            morph_texts = phrase_data[1:]
            morphs = []
            for morph_data in morph_texts:
                morph_dict = {}
                temp_lst = morph_data.split("\t")
                add_lst = temp_lst[1].split(",")
                morph_dict["surface"] = temp_lst[0]
                morph_dict["pos"] = add_lst[0]
                morph_dict["pos1"] = add_lst[1]
                morph_dict["pos2"] = add_lst[2]
                morph_dict["form1"] = add_lst[4]
                morph_dict["base"] = add_lst[-3]
                morph_dict["yomi"] = add_lst[-2]
                morphs.append(morph_dict)

            add_dict = {
                "ahead_pidx" : ahead_pidx,
                "main_midx" : main_midx,
                "morphs" : morphs
            }
            result.append(add_dict)
        return result
