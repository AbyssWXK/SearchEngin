# coding=utf-8
from classifiers import DictClassifier
from hello import Music
import os

path = "E:\Python\Search Engine\songs"  # 文件夹目录  
files1 = os.listdir(path)  # 得到文件夹下的所有文件名称  
for files2 in files1:  # 遍历文件夹  
    files3 = os.listdir(path + '\\' + files2)
    for files4 in files3:
        files5 = os.listdir(path + '\\' + files2+'\\'+files4)
        for file in files5:
            if os.path.isfile(path + '\\' + files2 + '\\' + files4+'\\' +file):
                d = DictClassifier()
                result = d.analysis_file(path + '\\' + files2 + '\\' + files4+'\\' +file, None)
                em1 = result['scoreai']
                em2 = result['scoree']
                em3 = result['scorehao']
                em4 = result['scorejing']
                em5 = result['scoreju']
                em6 = result['scorele']
                em7 = result['scorenu']
                em8 = 0
                em9 = 0
                em10 = 0
                mname = file[:-4]
                m = Music(mname,em1,em2,em3,em4,em5,em6,em7,em8,em9,em10)
                m.save_db()
