# pbp_parse2.py

import os
import json
import sys
import csv
import operator
from collections import OrderedDict
import errorManager as em
import re
import regex

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

# OOO : XXX
# exception : '타석이탈위반'(이름), 'BH'
# caution : mind searching priority!
# 다음 text 받기 전, 타자주자 설정 함
pa_results = ['1루타',
              '2루타',
              '3루타',
              '홈런',
              '볼넷',
              '삼진',
              '몸에 맞는 볼',
              '내야안타',
              # 번트안타
              '안타',
              '고의4구',
              # 낫아웃 -> 폭투 or 포일 or K
              '낫아웃 폭투',
              '낫아웃 포일',
              '낫아웃',
              '낫 아웃',
              '타구맞음',
              # 플라이 -> 아웃, 인필드, 희플, 파플, 실책(뒤에서 다룸)
              ' 플라이 아웃',
              '인필드플라이',
              '희생플라이 아웃',
              '희생플라이아웃',
              '파울플라이 아웃',
              # 땅볼 -> 아웃 or 출루
              '땅볼 아웃',
              '땅볼로 출루',
              # 라인드라이브 -> 아웃 or 실책(뒤에서 다룸)
              '라인드라이브 아웃',
              # 병살타 + 번트병살타
              '병살타',
              '희생번트 아웃',
              '쓰리번트',
              ' 번트 아웃',
              # 희생번트로 기록
              '희생번트 실책',
              # 희생번트로 기록
              '희생번트 야수선택',
              '야수선택',
              # 플라이 실책, 번트 실책, 라인드라이브 실책, 병살실책, 실책
              '실책',
              # 포수 실책으로 기록
              '타격방해',
              # 기타
              '부정타격',
              '삼중살']

# [0-9]+구 OO
ball_results = ['스트라이크',
                '볼',
                '타격',
                '번트파울',
                '번트헛스윙',
                '파울',
                '헛스윙',
                '파울실책',
                # 12초 룰 경고 입력 - 볼
                'C',
                '12초',
                # pass
                '판독']

runner_results = [
    # 사유 기록 : 케바케로 추가기록(도루실패, 보크, 폭투, 실책)
    # Next play : 아웃, 진루, 홈인
    # 도루실패아웃, 도루실패 기록하며~, 이중도루/삼중도루도 있음
    '도루실패',
    '도루 실패',
    # 보크로 진루/홈인
    '보크',
    # 폭투로 진루/홈인, 폭투사이 진루실패아웃
    '폭투',
    # 포일로 진루/홈인, 포일사이 진루실패아웃
    '포일',
    # 주루방해, 실책으로~(단순 실책) 진루/홈인
    '실책',
    # 도루로 진루/홈인, 이중도루/삼중도루도 있음
    '도루',
    # 견제사 아웃
    '견제사',
    # 기타 사유 - 기록 x
    '재치로',
    '다른주자',
    '타구맞음',
    '공과',
    # 기타
    '진루',
    '태그아웃',
    '포스아웃',
    # 나머지
    '아웃'
]

other_text = ['포수송구방해로 아웃',
              '수비방해로 인하여',
              '낫아웃 다른주자 수비',
              '합의판정',
              '합의 판정',
              ' 최초 ',
              '어필아웃',
              '스포츠맨쉽',
              '퇴장',
              '추월',
              '경고',
              '판독',
              '비디오',
              '부상으로 중단',
              '주루방해로 득점',
              '말벌',
              'LG 2루주자',
              '4심합의',
              '넘어지면서']

results = ['내야안타',
           '1루타',
           '2루타',
           '3루타',
           '홈런',
           '번트안타',
           '땅볼 아웃',
           '플라이 아웃',
           '병살타 아웃',
           '번트병살타 아웃',
           '라인드라이브 아웃',
           '희생번트 아웃',
           '쓰리번트 아웃',
           ' 번트 아웃',
           '삼중살 아웃',
           '부정타격 아웃',
           '삼진 아웃',
           '스트라이크 낫 아웃',
           '타구맞음 아웃',
           '땅볼로 출루',
           '야수선택으로 출루',
           '실책으로 출루',
           '타격방해로 출루']

pa = regex.compile('^\p{Hangul}+ : [\p{Hangul}|0-9|\ ]+')
pitch = regex.compile('^[0-9]+구 \p{Hangul}+')
runner = regex.compile('^[0-9]루주자 \p{Hangul}+ : [\p{Hangul}|0-9|\ ()->]+')
change = regex.compile('교체$')


class BallGame:
    # game status dict
    game_status = {
        'game_date': '00000000',

        # batter & pitcher
        'pitcher': None,
        'batter': None,

        # bats/throws; 0 for Left, 1 for Right
        'stand': 0,
        'throws': 0,

        # ball count & inning & score
        'inning': 1,
        # 0 for top, 1 for bot
        'inning_topbot': 0,
        'balls': 0,
        'strikes': 0,
        'outs': 0,
        'score_home': 0,
        'score_away': 0,

        # pitch & pa result
        # ?결과 나왔을 때만 기록?
        'pa_result': None,
        'pitch_result': None,

        # pfx data
        'pitch_type': None,
        'speed': None,
        'px': None,
        'pz': None,
        'pfx_x': None,
        'pfx_z': None,
        'release_x': None,
        'release_z': None,
        'sz_bot': None,
        'sz_top': None,

        # base
        'runner_1b': None,
        'runner_2b': None,
        'runner_3b': None,

        # home & away
        'home': None,
        'away': None,
        'stadium': None,
        'referee': None,

        # home field
        'home_p': None,
        'home_c': None,
        'home_1b': None,
        'home_2b': None,
        'home_3b': None,
        'home_ss': None,
        'home_lf': None,
        'home_cf': None,
        'home_rf': None,
        'home_dh': None,

        # away field
        'away_p': None,
        'away_c': None,
        'away_1b': None,
        'away_2b': None,
        'away_3b': None,
        'away_ss': None,
        'away_lf': None,
        'away_cf': None,
        'away_rf': None,
        'away_dh': None
    }

    def __init__(self, game_date=None):
        # do nothing
        # print()
        if game_date is not None:
            self.game_status['game_date'] = game_date

    def set_home_away(self, home, away):
        self.game_status['home'] = home
        self.game_status['away'] = away

    def set_referee(self, referee):
        self.game_status['referee'] = referee

    def set_stadium(self, stadium):
        self.game_status['stadium'] = stadium


##########

def parse_pa_result(text):
    # do something
    print(pa.search(text).group().split(':')[-1].strip())
    return True


def parse_pitch(text):
    # do something
    print(pitch.search(text).group().split(' ')[-1])
    return True


def parse_runner(text):
    # do something
    if not change.findall(text):
        print(runner.search(text).group().split(':')[-1].strip())
    return True


def parse_change(text):
    src_pattern = regex.compile('[\p{Hangul}|0-9]+ \p{Hangul}+ : ')
    dst_pattern = regex.compile('[\p{Hangul}|0-9|\ ]+ \(으\)로 교체')

    src = src_pattern.search(text).group()
    if src:
        src_pos = src.strip().split(' ')[0]
        src_name = src.strip().split(' ')[1]
    else:
        return False

    dst = dst_pattern.search(text).group()
    if dst:
        dst_pos = dst.strip().split(' ')[0]
        dst_name = dst.strip().split(' ')[1]
    else:
        return False

    # do something
    print('{} {} -> {} {}'.format(src_pos, src_name, dst_pos, dst_name))
    return True


def parse_text(text):
    if pa.search(text):
        return parse_pa_result(text)
    elif pitch.search(text):
        return parse_pitch(text)
    elif runner.search(text):
        return parse_runner(text)
    elif change.search(text):
        return parse_change(text)
    else:
        # do nothing
        return True


# main function
def parse_game(game):
    fp = open(game, 'r', encoding='utf-8')
    js = json.loads(fp.read(), encoding='utf-8', object_pairs_hook=OrderedDict)
    fp.close()

    ball_game = BallGame(game_date=game[:8])

    ball_game.set_home_away(game[10:12], game[8:10])

    #ball_game.set_referee()
    #ball_game.set_stadium()

    rl = js['relayList']

    # test variable
    total_pitches = 0

    keys = list(rl.keys())
    keys = [int(v) for v in keys]
    keys.sort()

    if keys is None:
        print('no keys')
        return False

    for k in keys:
        pa_text_set = rl[str(k)]['textOptionList']
        for i in range(len(pa_text_set)):
            text = pa_text_set[i]['text']

            if parse_text(text) is False:
                return False

    return True


def parse_main(args, lm=None):
    # parse arguments
    # test
    mon_start = args[0]
    mon_end = args[1]
    year_start = args[2]
    year_end = args[3]

    if lm is not None:
        lm.resetLogHandler()
        lm.setLogPath(os.getcwd())
        lm.setLogFileName('parse_pitch_log.txt')
        lm.cleanLog()
        lm.createLogHandler()
        lm.log('---- Relay Text Parse Log ----')

    if not os.path.isdir('pbp_data'):
        print('no data folder')
        return False

    os.chdir('pbp_data')

    for year in range(year_start, year_end + 1):
        if not os.path.isdir(str(year)):
            print('no year dir')
            os.chdir('..')
            return False

        os.chdir(str(year))

        for month in range(mon_start, mon_end + 1):
            if not os.path.isdir(str(month)):
                print('no month dir')
                os.chdir('../../')
                return False

            os.chdir(str(month))

            games = [f for f in os.listdir('.') if (os.path.isfile(f)) and\
                                                   (f.lower().find('relay.json') > 0) and\
                                                   (os.path.getsize(f) > 512)]
            if not len(games) > 0:
                print('no games')
                os.chdir('..')
                continue

            games.sort()

            for game in games:
                rc = parse_game(game)
                if rc is False:
                    print('parse game failure')
                    os.chdir('../../../')
                    return False

            # end
            os.chdir('..')

        # end
        os.chdir('..')

    # end
    os.chdir('..')
