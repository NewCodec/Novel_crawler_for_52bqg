
bqg_key_lines=('	一秒记住【笔趣阁','	www.52bqg.com】，精彩小说无弹窗免费阅读！')
bgq_key_words='<strong>最新章节全文阅读</strong>'

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
    print("开始清理"+Novel_name)
    keywords_len = len(bqg_key_lines)
    with open(Novel_name,'rb') as nf:
        fp = open('c_'+Novel_name,'wb')
        for line in nf.readlines():
            need_clean = False
            for i in range(keywords_len):
                if bqg_key_lines[i].encode('utf-8') in line:
                    need_clean = True
                    break
            if bgq_key_words.encode('utf-8') in line:
                line_d = StringByteDelete(line.decode('utf-8'),bgq_key_words)
                line = line_d.encode('utf-8')
            if need_clean == False:
                fp.write(line)
        fp.close()
    print("清理完成")
    

if __name__ == '__main__':
    NovelClean('test.txt',bqg_key_lines,bgq_key_words)