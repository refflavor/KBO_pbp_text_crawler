# pbp_download.py

import sys
import os
from urllib.request import urlopen
from bs4 import BeautifulSoup
import json
import re
import http.client
from urllib.parse import urlparse
import errorManager as em

regular_start = {
    '2012': '0407',
    '2013': '0330',
    '2014': '0329',
    '2015': '0328',
    '2016': '0401',
    '2017': '0331'
}

playoff_start = {
    '2012': '1008',
    '2013': '1008',
    '2014': '1019',
    '2015': '1010',
    '2016': '1021',
    '2017': '1010'
}


def print_progress(bar_prefix, mon_file_num, done, skipped):
    if mon_file_num > 30:
        progress_pct = (float(done + skipped) / float(mon_file_num))
        bar = '+' * int(progress_pct * 30) + '-' * (30 - int(progress_pct * 30))
        print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, (done + skipped), mon_file_num,
                                                   progress_pct * 100), end="")
    elif mon_file_num > 0:
        bar = '+' * (done + skipped) + '-' * (mon_file_num - done - skipped)
        print('\r{}[{}] {} / {}, {:2.1f} %'.format(bar_prefix, bar, (done + skipped), mon_file_num,
                                                   float(done + skipped) / float(mon_file_num) * 100),
              end="")


def check_url(url):
    p = urlparse(url)
    conn = http.client.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400


def pbp_download(mon_start, mon_end, year_start, year_end, lm=None):
    # set url prefix
    schedule_url_prefix = "http://sports.news.naver.com/kbaseball/schedule/index.nhn?month="
    relay_prefix = "http://sportsdata.naver.com/ndata/kbo/"
    lineup_prefix = "http://sports.news.naver.com/gameCenter/gameRecord.nhn?category=kbo&gameId="

    # make directory
    if not os.path.isdir("./pbp_data"):
        os.mkdir("./pbp_data")

    for year in range(year_start, year_end + 1):
        # make year directory
        if not os.path.isdir("./pbp_data/{0}".format(str(year))):
            os.mkdir("./pbp_data/{0}".format(str(year)))

        for month in range(mon_start, mon_end + 1):
            if month < 10:
                mon = '0{}'.format(str(month))
            else:
                mon = str(month)

            if not os.path.isdir("./pbp_data/{0}/{1}".format(str(year), mon)):
                os.mkdir("./pbp_data/{0}/{1}".format(str(year), mon))

    os.chdir("./pbp_data")
    # current path : ./pbp_data/

    print("##################################################")
    print("#######            GET PBP DATA            #######")
    print("##################################################")

    for year in range(year_start, year_end + 1):
        print("  for Year {0}... ".format(str(year)))

        for month in range(mon_start, mon_end + 1):
            if month < 10:
                mon = '0{}'.format(str(month))
            else:
                mon = str(month)
            os.chdir("{0}/{1}".format(str(year), mon))
            # current path : ./pbp_data/YEAR/MONTH/

            # get URL
            schedule_url = "{0}{1}&year={2}".format(schedule_url_prefix, str(month), str(year))

            # progress bar
            print("    Month " + str(month) + "... ")
            bar_prefix = '    Downloading: '
            print('\r%s[waiting]' % bar_prefix, end="")

            # open URL
            # get relay URL list, write in text file
            # all GAME RESULTS in month/year

            # '경기결과' 버튼을 찾아서 태그를 모두 리스트에 저장.
            schedule_html = urlopen(schedule_url).read()
            schedule_soup = BeautifulSoup(schedule_html, "lxml")
            schedule_button = schedule_soup.findAll('span', attrs={'class': 'td_btn'})

            # '경기결과' 버튼을 찾아서 태그를 모두 리스트에 저장.
            game_ids = []
            for btn in schedule_button:
                link = btn.a['href']
                suffix = link.split('gameId=')[1]
                game_ids.append(suffix)

            mon_file_num = sum(1 for gameID in game_ids if (2050 >= int(gameID[:4]) >= 2010))

            # gameID가 있는 게임은 모두 경기 결과가 있는 것으로 판단함
            # 중계 텍스트는 nsd 파일이 있는 경우만 count
            # 이를 위해 check_url 함수를 사용
            # done + skipped == mon_file_num 이다.
            done = 0
            skipped = 0

            lm.resetLogHandler()
            lm.setLogPath(os.getcwd() + '/log/')
            lm.setLogFileName('pbpDownloadLog.txt')
            lm.cleanLog()
            lm.createLogHandler()

            for gameID in game_ids:
                relay_link = relay_prefix + gameID[:4] + '/' + gameID[4:6] + '/' \
                             + gameID + '.nsd'

                lineup_url = "{}{}".format(lineup_prefix, gameID)

                if int(gameID[:4]) < 2010:
                    continue
                elif int(gameID[:4]) > 2050:
                    continue

                if int(regular_start[gameID[:4]]) > int(gameID[4:8]):
                    skipped += 1
                    continue

                if int(playoff_start[gameID[:4]]) <= int(gameID[4:8]):
                    skipped += 1
                    continue

                pbp_data_filename = gameID[0:13] + '_pbp.json'
                lineup_data_filename = gameID[0:13] + '_lineup.json'

                if not check_url(relay_link):
                    skipped = skipped + 1
                    continue
                elif (os.path.isfile(pbp_data_filename) and
                          (os.path.getsize(pbp_data_filename) > 0) and
                          os.path.isfile(lineup_data_filename) and
                          (os.path.getsize(lineup_data_filename) > 0)):
                    done += 1
                    continue
                else:
                    relay_html = urlopen(relay_link)
                    lineup_html = urlopen(lineup_url)

                    soup = BeautifulSoup(relay_html.read(), "lxml")
                    script = soup.find('script', text=re.compile('sportscallback_relay'))
                    try:
                        json_text = re.search(r'({"gameInfo":{.*?}}},.*?}}})', script.string, flags=re.DOTALL).group(1)
                    except AttributeError:
                        try:
                            json_text = re.search(r'({"awayTeamLineUp":{.*?}}},.*?}}\))', script.string,
                                                  flags=re.DOTALL).group(1)
                            json_text = json_text[:-1]
                        except AttributeError:
                            try:
                                json_text = re.search(r'({"games":.*?}}\))', script.string,
                                                      flags=re.DOTALL).group(1)
                                json_text = json_text[:-1]
                            except AttributeError:
                                print()
                                print('JSON parse error in : {}'.format(gameID))
                                print(em.getTracebackStr())
                                lm.bugLog('JSON parse error in : {}'.format(gameID))
                                lm.bugLog(em.getTracebackStr())
                                lm.killLogManager()
                                exit(1)

                    if sys.platform == 'win32':
                        data = json.loads(json_text, encoding='iso-8859-1')
                    else:
                        try:
                            data = json.loads(json_text)
                        except:
                            print()
                            print(json_text)
                            print(gameID)
                            exit(1)

                    # BUGBUG 20160506SKSS 김강민 2루수 플라이 아웃
                    # seqno 394인데 bb data 에는 393으로 기록. bb data 에 맞춤.
                    if gameID[:12] == '20160506SKSS':
                        data['relayTexts']['9'][1]['seqno'] = 393

                    with open(pbp_data_filename, 'w', encoding='utf-8') as pbp_data_file:
                        json.dump(data, pbp_data_file, indent=4, ensure_ascii=False)
                    pbp_data_file.close()

                    soup = BeautifulSoup(lineup_html.read(), 'lxml')
                    script = soup.find('script', text=re.compile('DataClass '))
                    try:
                        json_text = re.search(r'({"etcRecords":\[{.*?}}})', script.string, flags=re.DOTALL).group(1)
                    except AttributeError:
                        try:
                            json_text = re.search(r'({"games":\[{.*?}},"homeStandings":{.*?}})', script.string,
                                                  flags=re.DOTALL).group(1)
                        except AttributeError:
                            print()
                            print('JSON parse error in : {}'.format(gameID))
                            print(em.getTracebackStr())
                            lm.bugLog('JSON parse error in : {}'.format(gameID))
                            lm.bugLog(em.getTracebackStr())
                            lm.killLogManager()
                            exit(1)

                    if sys.platform == 'win32':
                        data = json.loads(json_text, encoding='iso-8859-1')
                    else:
                        data = json.loads(json_text)
                    with open(lineup_data_filename, 'w', encoding='utf-8') as lineup_data_file:
                        lineup_data_file.write(json.dumps(data, indent=4, ensure_ascii=False))
                    lineup_data_file.close()

                    done = done + 1
                    lm.log('{} download'.format(gameID))

                print_progress(bar_prefix, mon_file_num, done, skipped)
            print_progress(bar_prefix, mon_file_num, done, skipped)
            print()
            print('        Downloaded {0} files'.format(str(done)))
            print('        (Skipped {0} files)'.format(str(skipped)))
            os.chdir('../..')
            # current path : ./pbp_data/
    os.chdir('..')
    # current path : ./
    print("DOWNLOAD PBP DATA DONE.")
