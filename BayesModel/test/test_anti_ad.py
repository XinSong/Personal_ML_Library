#!/bin/env python
#coding=gbk
import sys
sys.path.append('bin')
sys.path.append('lib')
sys.path.append('conf')

import os
import unittest
import conf
sys.path.append(conf.APL_PATH)
import log

import anti_ad

def setUpModule():
    segdict_conf_path = conf.SEGDICT_CONF_PATH
    segdict_path = conf.SEGDICT_PATH
    global word_segger
    word_segger = anti_ad.WordSegger(segdict_conf_path, segdict_path)
    anti_ad.word_segger = word_segger


def tearDownModule(): 
    pass


def produce_comment(comments=None):
    f = open('comment.txt', 'w')
    if not comments:
        comments = [
            [100, 10, 1, '����1', '2014-04-11 00:00:00', 'www.baidu.com', '�ٶ�'],
            [200, 10, 1, '����2', '2014-04-11 00:00:00', 'www.baidu.com', '�ٶ�'],
        ]

    for comment in comments:
        comtid, siteid, ppid, content, addtime, lpurl, sitename = comment
        f.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (comtid, siteid, ppid, content, addtime, lpurl, sitename))
    f.close()


class TestLoadComment(unittest.TestCase):
    def test_normal(self):
        produce_comment()
        comments = anti_ad.load_comment('comment.txt')
        self.assertEqual(2, len(comments))

        comment = comments[0]
        self.assertEqual(100, comment.comtid)
        self.assertEqual(10, comment.siteid)
        self.assertEqual(1, comment.ppid)
        self.assertEqual('����1', comment.content)
        self.assertEqual('2014-04-11 00:00:00', comment.addtime)
        self.assertEqual('www.baidu.com', comment.lpurl)
        self.assertEqual('�ٶ�', comment.sitename)

        comment = comments[1]
        self.assertEqual(200, comment.comtid)
        self.assertEqual(10, comment.siteid)
        self.assertEqual(1, comment.ppid)
        self.assertEqual('����2', comment.content)
        self.assertEqual('2014-04-11 00:00:00', comment.addtime)
        self.assertEqual('www.baidu.com', comment.lpurl)
        self.assertEqual('�ٶ�', comment.sitename)


class TestWordSegger(unittest.TestCase):
    def test_get_words(self):
        contents = [
            '��������ƽ�ȱ�ݵػ�ȡ��Ϣ���ҵ�����',
            '�򵥿�����',
        ]
        
        content = contents[0]
        print ['��', '����', '��', 'ƽ��', '���', '��', '��ȡ', '��Ϣ', '��', '�ҵ�', '��', '��']
        self.assertEqual(word_segger.get_words(content),['��', '����', '��', 'ƽ��', '���', '��', '��ȡ', '��Ϣ', '��', '�ҵ�', '��', '��'])
       
        content = contents[1]
        self.assertEqual(word_segger.get_words(content), ['��', '��', '����'])


class TestBayesModel(unittest.TestCase):
    def test_predict(self):
        model = anti_ad.BayesModel(conf.TRAIN_NORMAL_PATH, conf.TRAIN_SPAM_PATH)

        review = '��ҹ�˾������ѵִ��ϵͳ����ѵ����Ҳ�����⣬����Ҫ������ѵЧ���ǳ���  ֵ���Ƽ�'
        review_words = word_segger.get_words(review)
        self.assertFalse(model.predict(review_words))

        review = '��Ҫ��ҵ��QQ���룺2594710125.�ֻ�����λ����΢�ż�¼��ѯ ��΢�ż�¼ɾ�� ������¼��ѯ��������¼ɾ�� QQ����*��¼��ѯ ɾ���ֻ��嵥��¼����������ɾ��ȫ�������ֻ���������Ϣ���ݡ������ʻ��嵥���������飬�ֻ� ɾ���ֻ��嵥��¼����������ɾ�� �ֻ�������Ϣ���ݣ�����ôɾ���ֻ��������ݡ��ƶ��ֻ��������ݡ���ͨ�ֻ��������ݣ���ô���ݡ��޸��ֻ�ͨ���嵥 �������ϸ�ı����ƶȺͽϷḻ�ľ��飬����������һ�е�Ҫ�������ѡ�����ǡ����š����ܡ���Ч�����ǵķ�����ּ�����ǵĳ�ŵ 00��Ϊί���ˣ���������κ�һ�ַ�ʽ֤���������õ����ü�¼'	
        review_words = word_segger.get_words(review)
        self.assertTrue(model.predict(review_words))
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
