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
    
    def tree2string(self, sentence):
        """
        解析の実行結果を標準出力のまま受け取るメソッド
        @ sentence: 係り受けしたい文
        """
        self.proc.stdin.write(bytes(sentence + '\n', self.encoding))
        self.proc.stdin.flush()
        # 出力を取得
        cabocha_out = []
        while True:
            line = self.proc.stdout.readline().decode(self.encoding)
            cabocha_out.append(line)
            if line.startswith("EOS"):
                break
                
        return "".join(cabocha_out)
    
    def tree2list(self, sentence):
        """
        解析の結果をリスト化して返す。
        @ sentence: 係り受けしたい文
        """
        cabocha_out = self.tree2string(sentence)
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
    
    def get_bf_morph_pairs(self, sentence):
        '''
        係り受け関係にある文節より基本形にした形態素ペアをリストで取得
        @ sentence: 係り受けしたい文
        '''
        phrases = self.tree2list(sentence)
        out_morph_pairs = list()
        # 文節毎に処理
        for pidx, phrase_data in enumerate(phrases):
            ahead_pidx = phrase_data["ahead_pidx"]
            main_midx = phrase_data["main_midx"]
            morphs = phrase_data["morphs"]
            # 係り先であれば何もしない
            if ahead_pidx != -1:
                dep_morphs = phrases[ahead_pidx]["morphs"]  # 係り先の形態素リスト
                dep_main_midx = phrases[ahead_pidx]["main_midx"]  # 係り先の主辞

                # 係り元の主辞が名詞であれば連続する名詞を原型にして取得
                if morphs[main_midx]["pos"] == "名詞" and not morphs[main_midx]["pos1"].startswith("形容動詞"):
                    morph_out = "".join([morph["surface"] for morph in morphs if morph["pos"] == "名詞"])
                else:
                    morph_out = morphs[main_midx]["base"]

                # 係り先の主辞が名詞であれば連続する名詞を原型にして取得
                if dep_morphs[dep_main_midx]["pos"] == "名詞" and not dep_morphs[dep_main_midx]["pos1"].startswith("形容動詞"):
                    dep_morph_out = "".join([dep_morph["surface"] for dep_morph in dep_morphs if dep_morph["pos"] == "名詞"])
                # 係り先が動詞の場合は前後を見る
                elif dep_morphs[dep_main_midx]["pos"].startswith("動詞"):
                    # 主辞の前を見ていく
                    count = 1
                    temp_morphs = [dep_morphs[dep_main_midx]["base"]]
                    while True:
                        check_idx = dep_main_midx - count
                        if check_idx < 0:
                            break
                        elif dep_morphs[check_idx]["pos"].startswith("名詞") or dep_morphs[check_idx]["pos"].startswith("動詞"):
                            temp_morphs.insert(0, dep_morphs[check_idx]["base"])
                        else:
                            break
                        count += 1
                    
                    count = 1   
                    while True:
                        check_idx = dep_main_midx + count
                        if check_idx == len(morphs):
                            break
                        elif dep_morphs[check_idx]["pos"].startswith("名詞") or dep_morphs[check_idx]["pos"].startswith("動詞"):
                            temp_morphs.append(dep_morphs[check_idx]["base"])
                        else:
                            break
                        count += 1
                    dep_morph_out = "".join(temp_morphs)
                else:
                    dep_morph_out = dep_morphs[dep_main_midx]["base"]

                one_pair = [morph_out, dep_morph_out]
                out_morph_pairs.append(one_pair)

        return out_morph_pairs
