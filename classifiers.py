# coding=UTF-8
import re
from collections import defaultdict
import jieba
import numpy as np
from jieba import posseg
import io
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# ################################################
# classifier based on sentiment f_dict
# ################################################
class DictClassifier:
    def __init__(self):
        self.__root_filepath = "f_dict/"

        # jieba.load_userdict("f_dict/user.dict")  # 准备分词词典

        # 准备情感词典词典
        self.__conjunction_dict = self.__get_dict(self.__root_filepath + "conjunction_dict.txt")
        self.__adverb_dict = self.__get_dict(self.__root_filepath + "adverb_dict.txt")
        self.__denial_dict = self.__get_dict(self.__root_filepath + "denial_dict.txt")
        self.__ai_dict = self.__get_dict(self.__root_filepath + "ai.txt")
        self.__e_dict = self.__get_dict(self.__root_filepath + "e.txt")
        self.__jing_dict = self.__get_dict(self.__root_filepath + "jing.txt")
        self.__hao_dict = self.__get_dict(self.__root_filepath + "hao.txt")
        self.__ju_dict = self.__get_dict(self.__root_filepath + "ju.txt")
        self.__le_dict = self.__get_dict(self.__root_filepath + "le.txt")
        self.__nu_dict = self.__get_dict(self.__root_filepath + "nu.txt")


    def classify(self, sentence):
        return self.analyse_sentence(sentence)

    def analysis_file(self, filepath_in, filepath_out, encoding="utf-8", print_show=True, start=0, end=-1):
        #open(filepath_out, "w")

        with open(filepath_in, "r", encoding=encoding) as f:
            results = self.analyse_sentence(f.read(), filepath_out, print_show)

        return results

    def analyse_sentence(self, sentence, runout_filepath=None, print_show=True):
        # 情感分析整体数据结构
        comment_analysis = {"su-clause":None,"scoreai": 0,"scoree": 0,"scorehao": 0,"scorejing": 0,"scoreju": 0,"scorele": 0,"scorenu": 0}

        # 将评论分句
        the_clauses = self.__divide_sentence_into_clauses(sentence + "%")

        # 对每分句进行情感分析
        for i in range(len(the_clauses)):
            # 情感分析子句的数据结构
            sub_clause = self.__analyse_clause(the_clauses[i].replace("。", "."), runout_filepath, print_show)
            # 将子句分析的数据结果添加到整体数据结构中
            comment_analysis["su-clause" + str(i)] = sub_clause
            comment_analysis['scoreai'] += sub_clause['scoreai']
            comment_analysis['scoree'] += sub_clause['scoree']
            comment_analysis['scorehao'] += sub_clause['scorehao']
            comment_analysis['scorejing'] += sub_clause['scorejing']
            comment_analysis['scoreju'] += sub_clause['scoreju']
            comment_analysis['scorele'] += sub_clause['scorele']
            comment_analysis['scorenu'] += sub_clause['scorenu']
            print(sub_clause)

        if runout_filepath is not None:
            # 将整句写进运行输出文件，以便复查
            self.__write_runout_file(runout_filepath, "\n" + sentence + '\n')
            # 将每个评论的每个分句的分析结果写进运行输出文件，以便复查
            self.__output_analysis(comment_analysis, runout_filepath)
            # 将每个评论的的整体分析结果写进运行输出文件，以便复查
            self.__write_runout_file(runout_filepath, str(comment_analysis) + "\n\n\n\n")
        if print_show:
            print("\n" + sentence)
            #self.__output_analysis(comment_analysis)
            print(comment_analysis)

        return comment_analysis

    def __analyse_clause(self, the_clause, runout_filepath, print_show):
        sub_clause = {"scoreai": 0,"scoree": 0,"scorehao": 0,"scorejing": 0,"scoreju": 0,"scorele": 0,"scorenu": 0,"score": 0, \
                      "ai": [],"e": [],"hao": [],"jing": [],"ju": [],"le": [],"nu": [],\
                       "conjunction": []}
        seg_result = posseg.lcut(the_clause)

        # 将分句及分词结果写进运行输出文件，以便复查
        if runout_filepath is not None:
            self.__write_runout_file(runout_filepath, the_clause + '\n')
            self.__write_runout_file(runout_filepath, str(seg_result) + '\n')
        if print_show:
            print(the_clause)
            print(seg_result)
        # 逐个分析分词
        for i in range(len(seg_result)):
            mark, result = self.__analyse_word(seg_result[i].word, seg_result, i)
            if mark == 0:
                continue
            elif mark == 1:
                sub_clause["conjunction"].append(result)
            elif mark == 2:
                sub_clause["ai"].append(result)
                sub_clause["scoreai"] += result["value"]
            elif mark == 3:
                sub_clause["e"].append(result)
                sub_clause["scoree"] += result["value"]
            elif mark == 4:
                sub_clause["hao"].append(result)
                sub_clause["scorehao"] += result["value"]
            elif mark == 5:
                sub_clause["jing"].append(result)
                sub_clause["scorejing"] += result["value"]
            elif mark == 6:
                sub_clause["ju"].append(result)
                sub_clause["scoreju"] += result["value"]
            elif mark == 7:
                sub_clause["le"].append(result)
                sub_clause["scorele"] += result["value"]
            elif mark == 8:
                sub_clause["nu"].append(result)
                sub_clause["scorenu"] += result["value"]

        # 综合连词的情感值
        for a_conjunction in sub_clause["conjunction"]:
            sub_clause["score"] *= a_conjunction["value"]

        return sub_clause

    def __analyse_word(self, the_word, seg_result=None, index=-1):
        # 判断是否是连词
        judgement = self.__is_word_conjunction(the_word)
        if judgement != "":
            return 1, judgement

        # 判断是否是正向情感词
        judgement = self.__is_word_ai(the_word, seg_result, index)
        if judgement != "":
            return 2, judgement

        judgement = self.__is_word_e(the_word, seg_result, index)
        if judgement != "":
            return 3, judgement

        judgement = self.__is_word_hao(the_word, seg_result, index)
        if judgement != "":
            return 4, judgement

        judgement = self.__is_word_jing(the_word, seg_result, index)
        if judgement != "":
            return 5, judgement

        judgement = self.__is_word_ju(the_word, seg_result, index)
        if judgement != "":
            return 6, judgement

        judgement = self.__is_word_le(the_word, seg_result, index)
        if judgement != "":
            return 7, judgement

        judgement = self.__is_word_nu(the_word, seg_result, index)
        if judgement != "":
            return 8, judgement

        return 0, ""

    def __is_word_conjunction(self, the_word):
        if the_word in self.__conjunction_dict:
            conjunction = {"key": the_word, "value": self.__conjunction_dict[the_word]}
            return conjunction
        return ""

    def __is_word_ai(self, the_word, seg_result, index):
        # 判断分词是否在情感词典内
        if the_word in self.__ai_dict:
            # 在情感词典内，则构建一个以情感词为中心的字典数据结构
            return self.__emotional_word_analysis(the_word, self.__ai_dict[the_word],
                                                  [x for x, y in seg_result], index)
        # 不在情感词典内，则返回空
        return ""

    def __is_word_e(self, the_word, seg_result, index):
        # 判断分词是否在情感词典内
        if the_word in self.__e_dict:
            # 在情感词典内，则构建一个以情感词为中心的字典数据结构
            return self.__emotional_word_analysis(the_word, self.__e_dict[the_word],
                                                  [x for x, y in seg_result], index)
        # 不在情感词典内，则返回空
        return ""

    def __is_word_hao(self, the_word, seg_result, index):
        # 判断分词是否在情感词典内
        if the_word in self.__hao_dict:
            # 在情感词典内，则构建一个以情感词为中心的字典数据结构
            return self.__emotional_word_analysis(the_word, self.__hao_dict[the_word],
                                                  [x for x, y in seg_result], index)
        # 不在情感词典内，则返回空
        return ""

    def __is_word_jing(self, the_word, seg_result, index):
        # 判断分词是否在情感词典内
        if the_word in self.__jing_dict:
            # 在情感词典内，则构建一个以情感词为中心的字典数据结构
            return self.__emotional_word_analysis(the_word, self.__jing_dict[the_word],
                                                  [x for x, y in seg_result], index)
        # 不在情感词典内，则返回空
        return ""

    def __is_word_ju(self, the_word, seg_result, index):
        # 判断分词是否在情感词典内
        if the_word in self.__ju_dict:
            # 在情感词典内，则构建一个以情感词为中心的字典数据结构
            return self.__emotional_word_analysis(the_word, self.__ju_dict[the_word],
                                                  [x for x, y in seg_result], index)
        # 不在情感词典内，则返回空
        return ""

    def __is_word_le(self, the_word, seg_result, index):
        # 判断分词是否在情感词典内
        if the_word in self.__le_dict:
            # 在情感词典内，则构建一个以情感词为中心的字典数据结构
            return self.__emotional_word_analysis(the_word, self.__le_dict[the_word],
                                                  [x for x, y in seg_result], index)
        # 不在情感词典内，则返回空
        return ""

    def __is_word_nu(self, the_word, seg_result, index):
        # 判断分词是否在情感词典内
        if the_word in self.__nu_dict:
            # 在情感词典内，则构建一个以情感词为中心的字典数据结构
            return self.__emotional_word_analysis(the_word, self.__nu_dict[the_word],
                                                  [x for x, y in seg_result], index)
        # 不在情感词典内，则返回空
        return ""


    def __emotional_word_analysis(self, core_word, value, segments, index):
        # 在情感词典内，则构建一个以情感词为中心的字典数据结构
        orientation = {"key": core_word, "adverb": [], "denial": [], "value": value}
        orientation_score = orientation["value"]  # my_sentiment_dict[segment]

        # 在三个前视窗内，判断是否有否定词、副词
        view_window = index - 1
        if view_window > -1:  # 无越界
            # 判断前一个词是否是情感词
            if segments[view_window] in self.__ai_dict or \
                    segments[view_window] in self.__e_dict or \
                    segments[view_window] in self.__hao_dict or \
                    segments[view_window] in self.__jing_dict or \
                    segments[view_window] in self.__ju_dict or \
                    segments[view_window] in self.__le_dict or \
                    segments[view_window] in self.__nu_dict:
                orientation["value"] = orientation_score
                return orientation
            # 判断是否是副词
            if segments[view_window] in self.__adverb_dict:
                # 构建副词字典数据结构
                adverb = {"key": segments[view_window], "position": 1,
                          "value": self.__adverb_dict[segments[view_window]]}
                orientation["adverb"].append(adverb)
                orientation_score *= self.__adverb_dict[segments[view_window]]
            # 判断是否是否定词
            elif segments[view_window] in self.__denial_dict:
                # 构建否定词字典数据结构
                denial = {"key": segments[view_window], "position": 1,
                          "value": self.__denial_dict[segments[view_window]]}
                orientation["denial"].append(denial)
                orientation_score *= -1
        view_window = index - 2
        if view_window > -1:
            # 判断前一个词是否是情感词
            if segments[view_window] in self.__ai_dict or \
                    segments[view_window] in self.__e_dict or \
                    segments[view_window] in self.__hao_dict or \
                    segments[view_window] in self.__jing_dict or \
                    segments[view_window] in self.__ju_dict or \
                    segments[view_window] in self.__le_dict or \
                    segments[view_window] in self.__nu_dict:
                orientation["value"] = orientation_score
                return orientation
            if segments[view_window] in self.__adverb_dict:
                adverb = {"key": segments[view_window], "position": 2,
                          "value": self.__adverb_dict[segments[view_window]]}
                orientation_score *= self.__adverb_dict[segments[view_window]]
                orientation["adverb"].insert(0, adverb)
            elif segments[view_window] in self.__denial_dict:
                denial = {"key": segments[view_window], "position": 2,
                          "value": self.__denial_dict[segments[view_window]]}
                orientation["denial"].insert(0, denial)
                orientation_score *= -1
                # 判断是否是“不是很好”的结构（区别于“很不好”）
                if len(orientation["adverb"]) > 0:
                    # 是，则引入调节阈值，0.3
                    orientation_score *= 0.3
        view_window = index - 3
        if view_window > -1:
            # 判断前一个词是否是情感词
            if segments[view_window] in self.__ai_dict or \
                    segments[view_window] in self.__e_dict or \
                    segments[view_window] in self.__hao_dict or \
                    segments[view_window] in self.__jing_dict or \
                    segments[view_window] in self.__ju_dict or \
                    segments[view_window] in self.__le_dict or \
                    segments[view_window] in self.__nu_dict:
                orientation["value"] = orientation_score
                return orientation
            if segments[view_window] in self.__adverb_dict:
                adverb = {"key": segments[view_window], "position": 3,
                          "value": self.__adverb_dict[segments[view_window]]}
                orientation_score *= self.__adverb_dict[segments[view_window]]
                orientation["adverb"].insert(0, adverb)
            elif segments[view_window] in self.__denial_dict:
                denial = {"key": segments[view_window], "position": 3,
                          "value": self.__denial_dict[segments[view_window]]}
                orientation["denial"].insert(0, denial)
                orientation_score *= -1
                # 判断是否是“不是很好”的结构（区别于“很不好”）
                if len(orientation["adverb"]) > 0 and len(orientation["denial"]) == 0:
                    orientation_score *= 0.3
        # 添加情感分析值。
        orientation["value"] = orientation_score
        # 返回的数据结构
        return orientation

    # 输出comment_analysis分析的数据结构结果
    def __output_analysis(self, comment_analysis, runout_filepath='test.txt'):
        output ="Scoreai:" + str(comment_analysis["scoreai"]) + " "\
        "Scoree:" + str(comment_analysis["scoree"]) + " "\
        "Scorehao:" + str(comment_analysis["scorehao"]) + " "\
        "Scorejing:" + str(comment_analysis["scorejing"]) + " "\
        "Scoreju:" + str(comment_analysis["scoreju"]) + " "\
        "Scorele:" + str(comment_analysis["scorele"]) + " "\
        "Scorenu:" + str(comment_analysis["scorenu"]) + "\n"

        for i in range(len(comment_analysis) - 1):
            output += "Sub-clause" + str(i) + ": "
            clause = comment_analysis["su-clause" + str(i)]
            if len(clause["conjunction"]) > 0:
                output += "conjunction:"
                for punctuation in clause["conjunction"]:
                    output += punctuation["key"] + " "
            if len(clause["ai"]) > 0:
                output += "ai:"
                for ai in clause["ai"]:
                    if len(ai["denial"]) > 0:
                        for denial in ai["denial"]:
                            output += denial["key"] + str(denial["position"]) + "-"
                    if len(ai["adverb"]) > 0:
                        for adverb in ai["adverb"]:
                            output += adverb["key"] + str(adverb["position"]) + "-"
                    output += ai["key"] + " "
            if len(clause["e"]) > 0:
                output += "e:"
                for e in clause["e"]:
                    if len(e["denial"]) > 0:
                        for denial in e["denial"]:
                            output += denial["key"] + str(denial["position"]) + "-"
                    if len(e["adverb"]) > 0:
                        for adverb in e["adverb"]:
                            output += adverb["key"] + str(adverb["position"]) + "-"
                    output += e["key"] + " "
            if len(clause["hao"]) > 0:
                output += "hao:"
                for hao in clause["hao"]:
                    if len(hao["denial"]) > 0:
                        for denial in hao["denial"]:
                            output += denial["key"] + str(denial["position"]) + "-"
                    if len(hao["adverb"]) > 0:
                        for adverb in hao["adverb"]:
                            output += adverb["key"] + str(adverb["position"]) + "-"
                    output += hao["key"] + " "
            if len(clause["jing"]) > 0:
                output += "jing:"
                for jing in clause["jing"]:
                    if len(jing["denial"]) > 0:
                        for denial in jing["denial"]:
                            output += denial["key"] + str(denial["position"]) + "-"
                    if len(jing["adverb"]) > 0:
                        for adverb in jing["adverb"]:
                            output += adverb["key"] + str(adverb["position"]) + "-"
                    output += jing["key"] + " "
            if len(clause["ju"]) > 0:
                output += "ju:"
                for ju in clause["ju"]:
                    if len(ju["denial"]) > 0:
                        for denial in ju["denial"]:
                            output += denial["key"] + str(denial["position"]) + "-"
                    if len(ju["adverb"]) > 0:
                        for adverb in ju["adverb"]:
                            output += adverb["key"] + str(adverb["position"]) + "-"
                    output += ju["key"] + " "
            if len(clause["le"]) > 0:
                output += "le:"
                for le in clause["le"]:
                    if len(le["denial"]) > 0:
                        for denial in le["denial"]:
                            output += denial["key"] + str(denial["position"]) + "-"
                    if len(le["adverb"]) > 0:
                        for adverb in le["adverb"]:
                            output += adverb["key"] + str(adverb["position"]) + "-"
                    output += le["key"] + " "
            if len(clause["nu"]) > 0:
                output += "nu:"
                for nu in clause["nu"]:
                    if len(nu["denial"]) > 0:
                        for denial in nu["denial"]:
                            output += denial["key"] + str(denial["position"]) + "-"
                    if len(nu["adverb"]) > 0:
                        for adverb in nu["adverb"]:
                            output += adverb["key"] + str(adverb["position"]) + "-"
                    output += nu["key"] + " "

            # if clause["pattern"] is not None:
            #     output += "pattern:" + clause["pattern"]["key"] + " "
            output += "\n"
        if runout_filepath is not None:
            self.__write_runout_file(runout_filepath, output)
        else:
            print(output)

    def __divide_sentence_into_clauses(self, the_sentence):
        the_clauses = self.__split_sentence(the_sentence)

        # 识别“是……不是……”句式
        pattern = re.compile(r"([，、。%！；？?,!～~.… ]*)([\u4e00-\u9fa5]*?(要|选)"
                             r"的.+(送|给)[\u4e00-\u9fa5]+?[，。！%；、？?,!～~.… ]+)")
        match = re.search(pattern, the_sentence.strip())
        if match is not None and len(self.__split_sentence(match.group(2))) <= 2:
            to_delete = []
            for i in range(len(the_clauses)):
                if the_clauses[i] in match.group(2):
                    to_delete.append(i)
            if len(to_delete) > 0:
                for i in range(len(to_delete)):
                    the_clauses.remove(the_clauses[to_delete[0]])
                the_clauses.insert(to_delete[0], match.group(2))

        # 识别“要是|如果……就好了”的假设句式
        pattern = re.compile(r"([，%。、！；？?,!～~.… ]*)([\u4e00-\u9fa5]*?(如果|要是|"
                             r"希望).+就[\u4e00-\u9fa5]+(好|完美)了[，。；！%、？?,!～~.… ]+)")
        match = re.search(pattern, the_sentence.strip())
        if match is not None and len(self.__split_sentence(match.group(2))) <= 3:
            to_delete = []
            for i in range(len(the_clauses)):
                if the_clauses[i] in match.group(2):
                    to_delete.append(i)
            if len(to_delete) > 0:
                for i in range(len(to_delete)):
                    the_clauses.remove(the_clauses[to_delete[0]])
                the_clauses.insert(to_delete[0], match.group(2))

        the_clauses[-1] = the_clauses[-1][:-1]
        return the_clauses

    @staticmethod
    def __split_sentence(sentence):
        pattern = re.compile("\[.*?]")
        sentence_af = re.sub(pattern, '.', sentence)
        pattern = re.compile("[，。%、！!？?,；～~.… , \[ \] ]+")

        split_clauses = pattern.split(sentence_af.strip())
        punctuations = pattern.findall(sentence_af.strip())
        try:
            split_clauses.remove("")
        except ValueError:
            pass
        punctuations.append("")

        clauses = [''.join(x) for x in zip(split_clauses, punctuations)]

        return clauses


    # 情感词典的构建
    @staticmethod
    def __get_dict(path, encoding="utf-8"):
        sentiment_dict = {}
        pattern = re.compile(r"\s+")
        with io.open(path, encoding=encoding) as f:
            for line in f:
                result = pattern.split(line.strip())
                if len(result) == 2:
                    sentiment_dict[result[0]] = float(result[1])
        return sentiment_dict

    @staticmethod
    def __write_runout_file(path, info, encoding="utf-8"):
        with open(path, "a", encoding=encoding) as f:
            f.write("%s" % info)


# d = DictClassifier()
# result = d.analyse_sentence('他们在痛苦中颤抖或者呻吟，我听惯了医院里的啜泣。')
# print(result)