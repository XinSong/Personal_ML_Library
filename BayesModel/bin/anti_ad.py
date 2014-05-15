#coding=gbk
import sys
sys.path.append('lib')
sys.path.append('conf')
import conf
sys.path.append(conf.APL_PATH)
import wordseg
import log

class BayesModel:
    '''@brief 进行广告和正常评论分类的贝叶斯模型'''

    def __init__(self, normal_model_path, spam_model_path):
        
        self.normal_word_prob = dict()
        self.spam_word_prob = dict()

        firstRecord = True  #每个文件的第一条记录是训练集中正样本或负样本的条数，用来计算默认概率
        for line in open(normal_model_path, 'r'):
            line = line.rstrip()
            try:
                if firstRecord:
                    self.normal_record_num = float(line)
                    self.normal_default_prob = 1/(float(line) + 2)
                    firstRecord = False
                else:
                    vec = line.split('\t')
                    self.normal_word_prob[vec[0]] = float(vec[1])
            except exception as e:
                log.warning("[Load TRAIN_NORMAL error! error=%s,filepath=%s,line=%s\t]", e, normal_model_path, line.strip('\n'))

        firstRecord = True
        for line in open(spam_model_path, 'r'):
            line = line.rstrip()
            try:
                if firstRecord:
                    self.spam_record_num = float(line)
                    self.spam_default_prob = 1/(float(line) + 2)
                    firstRecord = False
                else:
                    vec = line.split('\t')
                    self.spam_word_prob[vec[0]] = float(vec[1])

            except exception as e:
                log.warning("[Load TRAIN_SPAM error! error=%s, filepath=%s, line=%s\t]", e, spam_model_path, line.strip('\n'))
        try:
            self.normal_prior = self.normal_record_num /(self.normal_record_num + self.spam_record_num)
            self.spam_prior = self.spam_record_num /(self.normal_record_num + self.spam_record_num)
        except exception as e:
            log.warning("[BayesModel Prior Calculation Error! Zero Division?]")
    
    def predict(self, words):
        normal_prob = self.normal_prior
        spam_prob = self.spam_prior 
        words = set(words)
        for word in words:
            if word in self.normal_word_prob:
                normal_prob *= self.normal_word_prob[word]
            else:
                normal_prob *= self.normal_default_prob

        for word in words:
            if word in self.spam_word_prob:
                spam_prob *= self.spam_word_prob[word]
            else:
                spam_prob *= self.spam_default_prob

        if spam_prob >= normal_prob:
            return 1
        else:
            return 0

class Comment:
    '''@brief 评论类 '''

    def __init__(self, comtid, siteid, ppid, content, addtime, lpurl, sitename):
        '''
        @brief 构造函数
        @param comtid 评论id
        @param siteid 站点id
        @param ppid 用户id
        @param content 评论内容
        @param addtime 评论添加时间
        @param lpurl 登陆页地址
        @param sitename 站点名称
        '''
        self.comtid = comtid
        self.siteid = siteid
        self.ppid = ppid
        self.content = content
        self.addtime = addtime
        self.lpurl = lpurl
        self.sitename = sitename

    def __str__(self):
        '''
        @brief 生成字串
        '''
        return "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (self.comtid, self.siteid, self.ppid, self.content, self.addtime, self.lpurl, self.sitename)
    def __repr__(self):
        '''
        @brief 生成字串
        '''
        return self.__str__()

def load_comment(comment_filename):
    '''
    @brief 加载评论
    @detail　格式为tsv，各列为comtid, siteid, ppid, content, lpurl, sitename, addtime
    @param comment_filename 评论文件名
    @return comments 评论列表
    '''
    comments = []

    with open(comment_filename,'r') as f:
        for line in f:
            try:
                comtid, siteid, ppid, content, addtime, lpurl, sitename = line.strip('\n').split('\t')
                comtid = int(comtid)
                siteid = int(siteid)
                ppid = int(ppid)
                content = content.strip('\n')
                comment = Comment(comtid, siteid, ppid, content, addtime, lpurl, sitename)
                comments.append(comment)
            except Exception as e:
                log.warning("[Load Comment File Error! error=%s, filename=%s, line=%s]", e, comment_filename, line.rstrip('\n'))

    return comments


class WordSegger:
    # 字符类型
    CharType = {
        'num': 1,
        'zh': 2,
        'en': 3,
        'sym': 4,
    }


    def __init__(self, segdict_conf_path, segdict_path):
        '''
        @brief 构造函数
        @param segdict_conf_path 配置文件位置
        @param segdict_path 切词库位置
        @param tagdict_path 词性库位置
        '''
        self.max_term_count = 512
        try:
            self.conf_handle = wordseg.scw_load_conf(segdict_conf_path)
            self.dict_handle = wordseg.scw_load_worddict(segdict_path)
            self.result_handle = wordseg.scw_create_out(self.max_term_count*10)
            self.token_handle = wordseg.create_tokens(self.max_term_count)
            self.token_handle = wordseg.init_tokens(self.token_handle, self.max_term_count)
        except Exception as e:
            log.warning("SegDict Load Error! error=%s",e);
        
    def get_words(self, content):
        '''
        @brief 取得分词结果
        @param content 文本内容
        @return 分词结果，以列表形式返回
        '''

        ANGTYPE_SIMP_CHINESE = 1 # 语言类型，简体中文为1，详细参见ul_ccode.h
        succ = 1
        if (succ == wordseg.scw_segment_words(self.dict_handle, self.result_handle, content,
                                              ANGTYPE_SIMP_CHINESE)):
            token_count = wordseg.scw_get_token_1(self.result_handle, wordseg.SCW_BASIC,
                                                  self.token_handle, self.max_term_count)
            token_list = wordseg.tokens_to_list(self.token_handle, token_count)
            word_list = [token[7] for token in token_list]
            return word_list
        else:
            log.warning("[Segment Word Fail! func=scw_segment_words,content=%s", content)
            return []

def main():
    if len(sys.argv) != 2:
        print >> sys.stderr, ("Usage: %s comment_filename" % sys.argv[0])
        sys.exit(1)
    else:
        from conf import LOG_LEVEL, LOG_FILENAME, WF_LOG_FILENAME
        from conf import SEGDICT_CONF_PATH, SEGDICT_PATH
        from conf import TRAIN_NORMAL_PATH, TRAIN_SPAM_PATH

        log.init(LOG_LEVEL, LOG_FILENAME, WF_LOG_FILENAME)
        comment_file = sys.argv[1]
        
        global word_segger
        word_segger = WordSegger(SEGDICT_CONF_PATH, SEGDICT_PATH)
        model = BayesModel(TRAIN_NORMAL_PATH, TRAIN_SPAM_PATH)

        comments = load_comment(comment_file)
        for comment in comments:
            words = word_segger.get_words(comment.content)
            print '%s\t%s' % (comment,model.predict(words))

if __name__ == "__main__":
    main()
