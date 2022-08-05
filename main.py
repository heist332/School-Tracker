import requests
from base64 import b64decode, b64encode

from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA

from typing import Dict

import aiohttp
from aiohttp.client_exceptions import ServerDisconnectedError

import asyncio

import sys


async def send_hcsreq(
    headers: Dict,
    endpoint: str,
    school: str,
    json: Dict,
    session: aiohttp.ClientSession,
):
    for attempt in range(5):
        try:
            async with session.post(
                headers=headers,
                url=f"https://{school}hcs.eduro.go.kr{endpoint}",
                json=json,
            ) as resp:
                return await resp.json()
        except ServerDisconnectedError as e:
            if attempt >= 4:
                raise e
            continue


# 모든 시/도개수 = 1~18개
# 학교급 = 2~4
#loginType: school

areas = {
    "area1": ["서울", "서울시", "서울교육청", "서울시교육청", "서울특별시", "서울특별시교육청"],
    "area2": ["부산", "부산광역시", "부산시", "부산교육청", "부산광역시교육청"],
    "area3": ["대구", "대구광역시", "대구시", "대구교육청", "대구광역시교육청"],
    "area4": ["인천", "인천광역시", "인천시", "인천교육청", "인천광역시교육청"],
    "area5": ["광주", "광주광역시", "광주시", "광주교육청", "광주광역시교육청"],
    "area6": ["대전", "대전광역시", "대전시", "대전교육청", "대전광역시교육청"],
    "area7": ["울산", "울산광역시", "울산시", "울산교육청", "울산광역시교육청"],
    "area8": ["세종", "세종특별시", "세종시", "세종교육청", "세종특별자치시", "세종특별자치시교육청"],
    "area10": ["경기", "경기도", "경기교육청", "경기도교육청"],
    "area11": ["강원", "강원도", "강원교육청", "강원도교육청"],
    "area12": ["충북", "충청북도", "충북교육청", "충청북도교육청"],
    "area13": ["충남", "충청남도", "충남교육청", "충청남도교육청"],
    "area14": ["전북", "전라북도", "전북교육청", "전라북도교육청"],
    "area15": ["전남", "전라남도", "전남교육청", "전라남도교육청"],
    "area16": ["경북", "경상북도", "경북교육청", "경상북도교육청"],
    "area17": ["경남", "경상남도", "경남교육청", "경상남도교육청"],
    "area18": ["제주", "제주도", "제주특별자치시", "제주교육청", "제주도교육청", "제주특별자치시교육청", "제주특별자치도"],
}


levels = {
    "level1": ["유치원", "유", "유치"],
    "level2": ["초등학교", "초", "초등"],
    "level3": ["중학교", "중", "중등"],
    "level4": ["고등학교", "고", "고등"],
    "level5": ["특수학교", "특", "특수", "특별"],
}


def schoolinfo(area):
    info = {}
    if area in areas["area1"]:
        schoolcode = "01"
        schoolurl = "sen"
    if area in areas["area2"]:
        schoolcode = "02"
        schoolurl = "pen"
    if area in areas["area3"]:
        schoolcode = "03"
        schoolurl = "dge"
    if area in areas["area4"]:
        schoolcode = "04"
        schoolurl = "ice"
    if area in areas["area5"]:
        schoolcode = "05"
        schoolurl = "gen"
    if area in areas["area6"]:
        schoolcode = "06"
        schoolurl = "dje"
    if area in areas["area7"]:
        schoolcode = "07"
        schoolurl = "use"
    if area in areas["area8"]:
        schoolcode = "08"
        schoolurl = "sje"
    if area in areas["area10"]:
        schoolcode = 10
        schoolurl = "goe"
    if area in areas["area11"]:
        schoolcode = 11
        schoolurl = "kwe"
    if area in areas["area12"]:
        schoolcode = 12
        schoolurl = "cbe"
    if area in areas["area13"]:
        schoolcode = 13
        schoolurl = "cne"
    if area in areas["area14"]:
        schoolcode = 14
        schoolurl = "jbe"
    if area in areas["area15"]:
        schoolcode = 15
        schoolurl = "jne"
    if area in areas["area16"]:
        schoolcode = 16
        schoolurl = "gbe"
    if area in areas["area17"]:
        schoolcode = 17
        schoolurl = "gne"
    if area in areas["area18"]:
        schoolcode = 18
        schoolurl = "jje"

    return schoolcode


def levelinfo(level):
    if level in levels["level1"]:
        schoollevel = 1
    if level in levels["level2"]:
        schoollevel = 2
    if level in levels["level3"]:
        schoollevel = 3
    if level in levels["level4"]:
        schoollevel = 4
    if level in levels["level5"]:
        schoollevel = 5
    return schoollevel


f = open('data.txt', 'r', encoding='utf-8')
dt = f.read()
print(dt.split('\n'))
births = dt.split('\n')[0]
names = dt.split('\n')[1]
se = dt.split('\n')[2]
school_rank = dt.split('\n')[3]
keyword = dt.split('\n')[4:]
f.close()

pubkey = (
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA81dCnCKt0NVH7j5Oh2"
    "+SGgEU0aqi5u6sYXemouJWXOlZO3jqDsHYM1qfEjVvCOmeoMNFXYSXdNhflU7mjWP8jWUmkYIQ8o3FGqMzsMTNxr"
    "+bAp0cULWu9eYmycjJwWIxxB7vUwvpEUNicgW7v5nCwmF5HS33Hmn7yDzcfjfBs99K5xJEppHG0qc"
    "+q3YXxxPpwZNIRFn0Wtxt0Muh1U8avvWyw03uQ/wMBnzhwUC8T4G5NclLEWzOQExbQ4oDlZBv8BM"
    "/WxxuOyu0I8bDUDdutJOfREYRZBlazFHvRKNNQQD2qDfjRz484uFs7b5nykjaMB9k/EJAuHjJzGs9MMMWtQIDAQAB== "
)


def encrypt(n):
    rsa_public_key = b64decode(pubkey)
    pub_key = RSA.importKey(rsa_public_key)
    cipher = Cipher_pkcs1_v1_5.new(pub_key)
    msg = n.encode("utf-8")
    length = 245

    msg_list = [msg[i: i + length] for i in list(range(0, len(msg), length))]

    encrypt_msg_list = [
        b64encode(cipher.encrypt(message=msg_str)) for msg_str in msg_list
    ]

    return encrypt_msg_list[0].decode("utf-8")


async def main():
    sess = requests.session()
    stats = False
    schoolcode = None
    for key in keyword:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=f"https://hcs.eduro.go.kr/v2/searchSchool?lctnScCode={schoolinfo(se)}&schulCrseScCode={levelinfo(school_rank)}&orgName={key}&loginType=school"
                ) as resp:
                    school_infos = await resp.json()
        except:
            await asyncio.sleep(2)

        if len(school_infos["schulList"]) > 5:
            print({
                "error": True,
                "code": "NOSCHOOL",
                "message": "너무 많은 학교가 검색되었습니다. 지역, 학교급을 제대로 입력하고 학교 이름을 보다 상세하게 적어주세요.",
            })
            break

        try:
            schoolcode = school_infos["schulList"][0]["orgCode"]
            name = encrypt(names)  # Encrypt Name
            birth = encrypt(births)  # Encrypt Birth
            endpnt = 'https://' + school_infos['schulList'][0]["atptOfcdcConctUrl"]


            try:
                res = requests.post(
                    headers={"Content-Type": "application/json"},
                    url=endpnt + "/v2/findUser",
                    json={
                        "orgCode": schoolcode,
                        "name": name,
                        "birthday": birth,
                        "loginType": "school",
                        "stdntPNo": None,
                    },
                )

                school_name = res.json()['orgName']
                username = res.json()['userName']
                print(f'유저를 발견했습니다.\n이름: {username}\n학교명: {school_name}\n생년월일: {births}')
                break

            except Exception as e:
                print({
                    "error": True,
                    "code": "NOSTUDENT",
                    "message": "학교는 검색하였으나, 입력한 정보의 학생을 찾을 수 없습니다.",
                })

        except Exception as e:
            print({
                "error": True,
                "code": "NOSCHOOL",
                "message": "검색 가능한 학교가 없습니다. 지역, 학교급을 제대로 입력하였는지 확인해주세요.",
            })
                

        


asyncio.run(main())
