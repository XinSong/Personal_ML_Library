#coding=gbk
import sys
sys.path.append('lib')
sys.path.append('conf')
import conf
sys.path.append(conf.APL_PATH)
import wordseg
import log

class BayesModel:
    '''@brief ���й����������۷���ı�Ҷ˹ģ��'''

    def __init__(self, normal_model_path, spam_model_path):
        
        self.normal_word_prob = dict()
        self.spam_word_prob = dict()

        firstRecord = True  #ÿ���ļ��ĵ�һ����¼��ѵ����������������������������������Ĭ�ϸ���
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
    '''@brief ������ '''

    def __init__(self, comtid, siteid, ppid, content, addtime, lpurl, sitename):
        '''
        @brief ���캯��
        @param comtid ����id
        @param siteid վ��id
        @param ppid �û�id
        @param content ��������
        @param addtime �������ʱ��
        @param lpurl ��½ҳ��ַ
        @param sitename վ������
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
        @brief �����ִ�
        '''
        return "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (self.comtid, self.siteid, self.ppid, self.content, self.addtime, self.lpurl, self.sitename)
    def __repr__(self):
        '''
        @brief �����ִ�
        '''
        return self.__str__()

def load_comment(comment_filename):
    '''
    @brief ��������
    @detail����ʽΪtsv������Ϊcomtid, siteid, ppid, content, lpurl, sitename, addtime
    @param comment_filename �����ļ���
    @return comments �����б�
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
    # �ַ�����
    CharType = {
        'num': 1,
        'zh': 2,
        'en': 3,
        'sym': 4,
    }


    def __init__(self, segdict_conf_path, segdict_path):
        '''
        @brief ���캯��
        @param segdict_conf_path �����ļ�λ��
        @param segdict_path �дʿ�λ��
        @param tagdict_path ���Կ�λ��
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
        @brief ȡ�÷ִʽ��
        @param content �ı�����
        @return �ִʽ�������б���ʽ����
        '''

        ANGTYPE_SIMP_CHINESE = 1 # �������ͣ���������Ϊ1����ϸ�μ�ul_ccode.h
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
