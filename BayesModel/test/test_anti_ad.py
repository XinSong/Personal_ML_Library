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
            [100, 10, 1, '评论1', '2014-04-11 00:00:00', 'www.baidu.com', '百度'],
            [200, 10, 1, '评论2', '2014-04-11 00:00:00', 'www.baidu.com', '百度'],
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
        self.assertEqual('评论1', comment.content)
        self.assertEqual('2014-04-11 00:00:00', comment.addtime)
        self.assertEqual('www.baidu.com', comment.lpurl)
        self.assertEqual('百度', comment.sitename)

        comment = comments[1]
        self.assertEqual(200, comment.comtid)
        self.assertEqual(10, comment.siteid)
        self.assertEqual(1, comment.ppid)
        self.assertEqual('评论2', comment.content)
        self.assertEqual('2014-04-11 00:00:00', comment.addtime)
        self.assertEqual('www.baidu.com', comment.lpurl)
        self.assertEqual('百度', comment.sitename)


class TestWordSegger(unittest.TestCase):
    def test_get_words(self):
        contents = [
            '让人们最平等便捷地获取信息，找到所求',
            '简单可依赖',
        ]
        
        content = contents[0]
        print ['让', '人们', '最', '平等', '便捷', '地', '获取', '信息', '，', '找到', '所', '求']
        self.assertEqual(word_segger.get_words(content),['让', '人们', '最', '平等', '便捷', '地', '获取', '信息', '，', '找到', '所', '求'])
       
        content = contents[1]
        self.assertEqual(word_segger.get_words(content), ['简单', '可', '依赖'])


class TestBayesModel(unittest.TestCase):
    def test_predict(self):
        model = anti_ad.BayesModel(conf.TRAIN_NORMAL_PATH, conf.TRAIN_SPAM_PATH)

        review = '这家公司不错，培训执行系统，培训基地也很满意，最重要的是培训效果非常好  值得推荐'
        review_words = word_segger.get_words(review)
        self.assertFalse(model.predict(review_words))

        review = '主要的业务：QQ号码：2594710125.手机定、位、、微信记录查询 ，微信记录删除 开房记录查询，开房记录删除 QQ聊天*记录查询 删除手机清单记录、短信内容删除全国各种手机、、短信息内容、银行帐户清单、婚姻调查，手机 删除手机清单记录，短信内容删除 手机（短消息内容）、怎么删除手机短信内容、移动手机短信内容、联通手机短信内容，怎么内容。修改手机通话清单 我们有严格的保密制度和较丰富的经验，尽力完善你一切的要求，请放心选择我们。诚信、保密、高效是我们的服务宗旨，我们的承诺 00作为委托人，如果您有任何一种方式证明您有良好的信用记录'	
        review_words = word_segger.get_words(review)
        self.assertTrue(model.predict(review_words))
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
