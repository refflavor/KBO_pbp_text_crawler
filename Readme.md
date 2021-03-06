﻿# 개요
[Naver](https://www.naver.com)의 문자 중계 시스템에서 pbp 데이터, 타구 데이터를 가져와 정리하여 csv 파일로 출력한다.

상세 내용은 추가 기술 예정.

아래 내용은 타구 정보만 가져오던 시절 것으로 out of date.

- 2017/10/31

# 개요(구 판본)

[Naver](https://www.naver.com)의 문자 중계 시스템에서 파일을 가져오고 parsing을 거쳐 타구 정보를 수집한다.

프로그램은 2개로 구성되어 있다. 하나는 경기결과에서 타구 위치를 읽어오는 용도고

다른 하나는 문자중계를 읽어와 상황 정보를 재구성하는데 필요한 데이터를 읽어온다.

결과물로는 시즌 전체 경기에서 나온 타구의 위치 정보, 타구가 나온 상황의 경기/선수 정보를 담은 csv 파일이 생성된다.

둘 다 python interpreter로 실행하면 된다.

# 요구 사항
- [Python 3](https://www.python.org/downloads/)
  * Python Modules : [lxml](http://lxml.de/), [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- OS: Windows, OS X, Linux
- 인터넷 연결 필요
- 커맨드라인 인터페이스(CLI)에서 실행 권장. 기타 환경에서 테스트한 적 없음.


# 파일 설명
실행에 필요한 파일 2개에 대한 설명만 정리한다.

## 실행 순서
bb.py를 실행해 타구 정보를 다운로드한다.

이후 pbp.py를 실행해 문자 중계 정보를 다운로드 & parsing한다.

pbp.py에서 다운로드한 정보를 토대로 타구가 나온 상황을 재구성한 뒤,
    
bb.py에서 다운로드한 타구 좌표를 대입해 csv파일을 생성한다.

## bb.py
Naver 문자 중계 시스템의 경기결과 탭에서 타구 정보를 추출해 JSON파일 형식으로 저장한다.

Default로 타구정보만을 정리한 csv 파일을 생성하도록 되어 있다.

옵션을 주면 csv파일 생성 없이 JSON파일만 생성한다.

- [Naver 문자중계창 경기결과 예시](http://sports.news.naver.com/gameCenter/gameResult.nhn?category=kbo&gameId=20170611WOHT02017)


## pbp.py
문자중계, 즉 play by play 데이터를 읽어온다.

중계를 JSON 형식으로 저장한 뒤 저장된 타구정보 JSON 파일을 읽어 정보를 재조합한다.

결과물로 타구 정보가 담긴 csv파일을 생성한다.

파일은 경기단위/월단위/연단위로 생성된다.

Default 저장경로는 실행경로 하위의 pbp\_data 디렉토리이며 경로가 없을 시 자동 생성된다.


# 실행 방법
커맨드라인 상에서 다음과 같이 입력한다.

```
pbp.py [시작 월] [끝 월] [시작 연도] [끝 연도] [-c] [-d]
```

bb.py도 실행 형식은 같다.

- 시작/끝 기간은 순서 상관 없이 입력해도 된다. 예를 들어 2016 2017 10 4 이렇게 입력하면 2016 & 2017년 3월부터 10월까지 해당되는 데이터를 모두 추출한다.
- 시작/끝은 4~10월만 가능. 그 밖에는 테스트한 적 없음.
- 정규시즌과 포스트시즌 구분 아직 없음.
- 시범경기 구간 제외하지 않았기 때문에 포함될 수 있다.
- '-c' 옵션을 주면 다운로드된 데이터만 가지고 csv파일로 변환하는 것만 수행한다.
-- 데이터가 없을 때 정상작동 보장하지 않는다.
- '-d' 옵션을 주면 JSON형식으로 데이터 다운로드&저장만 한다.
- '-c'와 '-d'를 모두 주면 다운로드 및 변환을 모두 수행한다.

실행 후 타구좌표와 타구 발생시 상황이 모두 담긴 데이터는 pbp\_data 경로 아래에 저장된다.


# 문제 해결
시즌 중, 월 단위 경기가 모두 끝나지 않았을 때는 bb.py / pbp.py 실행시 다운로드 도중 에러가 발생한다.

예를 들어 6월 11일에 6월 경기 데이터 다운로드를 실행하면 도중에 에러가 발생한다.

이는 정상적인 작동이니 개의치않고 다운로드 후 -c 옵션을 줘서 CSV로 변환을 별도로 수행하면 된다.

알아서 멈추게 해야하는데 아직 거기까지 수정하지 않았다.


# Tableau를 통한 시각화
Tableau를 통해 데이터 시각화를 진행하고 있다. [사이트](https://public.tableau.com/profile/yagongso#!/vizhome/KBObattedballmap2017/1)

배경화면으로는 Naver 경기결과 탭에서 타구정보를 표시할 때 쓰는 [이미지](http://imgnews.naver.net/image/sports/nsports/2010/bg_ground.jpg)를 사용했다.

Tableau를 사용할 때 다음 주의사항을 지키면 된다.

- X좌표는 0~445의 범위로 주어진다. 배경 이미지 X좌표 설정을 여기에 맞춰 왼쪽 0, 오른쪽 445로 설정한다.
- Y좌표는 0~415의 범위로 주어진다. 다만 홈플레이트가 0 방향이며, 12 정도 offset을 주어야 Naver에서 볼 수 있는 그림과 일치한다. 배경 이미지 Y좌표 설정을 위 403, 아래 -12로 한다.
- 이미지 Y좌표는 0\~415로 주어지지만 일부 점은 0보다 작은 값이 찍힌다. 때문에 Y축은 고정 축 범위를 -30\~415 정도로 준다.

![실제 적용된 이미지](http://i.imgur.com/FH8eMTs.jpg)

이 밖에 표시정보, 색상 선택, 모양 선택 등은 개인의 자유.
