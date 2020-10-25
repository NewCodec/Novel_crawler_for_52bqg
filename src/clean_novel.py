
import os
import sys

bqg_key_lines=('	一秒记住【笔趣阁','	www.52bqg.net】，精彩小说无弹窗免费阅读！')
bgq_key_words=['<strong>','最新章节全文阅读','</strong>','reads;','[棉花糖小说网www.Mianhuatang.com想看的书几乎都有啊，比一般的站要稳定很多更新还快，全文字的没有广告。]','[棉花糖小说网Mianhuatang.cc','更新快，网站页面清爽，广告少，，最喜欢这种网站了，一定要好评]','[看本书最新章节请到棉花糖小说网www.mianhuatang.cc]','更新好快。','（79小說网首发）','广告）。','79小說网首发','本书来自','品&书','[更新快，网站页面清爽，广告少，，最喜欢这种网站了，一定要好评]','$>>>棉、花‘糖’小‘說’)']

#str2 较短
#如果str1中有str2，则删除，否则什么也不做
def StringByteDelete(str1,str2):
    str1_len = len(str1)
    str1_index = 0
    
    str2_len = len(str2)
    if str1_len < str2_len:
        return str1
    for i in range(str1_len):
        if str1[i] == str2[0]:
            str1_index=i
            if str1_len-i < str2_len:
                return str1
            for j in range(str2_len):
                if str1[i+j] != str2[j]:
                    break
            if j ==str2_len-1:
                str1 = str1[0:str1_index]+str1[str1_index+str2_len:str1_len]
                return StringByteDelete(str1,str2)
            else:
                continue
    return str1

def NovelClean(Novel_name,bqg_key_lines,bgq_key_words):
    print("开始执行一些清理....")
    keywords_len = len(bqg_key_lines)
    with open(Novel_name,'rb') as nf:
        fp = open(Novel_name+'.temp','wb')
        for line in nf.readlines():
            need_clean = False
            line_d = line.decode('utf-8')
            for i in range(keywords_len):
                if bqg_key_lines[i].encode('utf-8') in line:
                    need_clean = True
                    break
            
            for j in range(len(bgq_key_words)):
                if bgq_key_words[j].encode('utf-8') in line:
                    line_d = StringByteDelete(line.decode('utf-8'),bgq_key_words[j])
                    line = line_d.encode('utf-8')
            line = line_d.encode('utf-8')
            if need_clean == False:
                fp.write(line)
        fp.close()
    os.remove(Novel_name)
    os.rename(Novel_name+'.temp',Novel_name)
    print("清理完成...")
    

if __name__ == '__main__':
    NovelClean(sys.argv[1],bqg_key_lines,bgq_key_words)