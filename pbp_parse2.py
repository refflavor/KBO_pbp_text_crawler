# pbp_parse2.py

import os
import json
import sys
import csv
import operator
from collections import OrderedDict
import errorManager as em
import re


pos_string = ["투수", "포수", "1루수", "2루수", "3루수",
              "유격수", "좌익수", "중견수", "우익수",
              "지명타자", "대타", "대주자"]

bb_dir_string = ["투수", "포수", "1루수", "2루수", "3루수",
                 "유격수", "좌익수", "중견수", "우익수",
                 "우중간", "좌중간"]

res_string = ["1루타", "안타" "2루타", "3루타", "홈런", "실책", "땅볼",
              "뜬공", "희생플라이", "희생번트", "야수선택", "삼진",
              "낫아웃", "타격방해", "직선타", "병살타", "번트", "내야안타"]

hit_results = ['안타', '1루타', '2루타', '3루타', '홈런']

out_results = ['땅볼', '플라이', '병살타', '라인드라이브',
               ' 번트', '희생번트', '삼중살']

nobb_outs = ['삼진', '낫 아웃', '타구맞음', '쓰리번트', '부정타격']

runner_outs = ['견제사', '  포스아웃', '  태그아웃',
               '도루실패', '진루실패', '터치아웃', '공과']

pass_games = ['20130609HHSK', '20130611LGHH', '20170509KTHT', '20130619LGNC',
              '20130912HTLG', '20140829LGSK', '20141017LGLT', '20150426LGNC',
              '20150505LGOB', '20150612LGHH', '20120513LTHH', '20120601HHLG',
              '20120603HHLG', '20120607LGWO', '20120613SKLG', '20120621LGHH',
              '20120630LGSK', '20120719SKLG', '20120725LGOB']
