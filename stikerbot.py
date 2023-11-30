import pandas as pd
import telegram as tel
from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler
from telegram.ext import filters
from telegram.ext import Application
import asyncio

import os
import sys
import con_crawler, con_upscaler

import re

df = pd.read_csv("./telegramapi.txt", sep=" ", header=None)

# api_token = df[1][0]
# chat_id = df[1][1]

API_TOKEN = df[1][0]
CHAT_ID = df[1][1]

bot = tel.Bot(token=API_TOKEN)

print("application 빌드")
application = Application.builder().token(API_TOKEN).build()
print("application 빌드 완료")

# 예제
# async def handler(update, context):
#     user_text = update.message.text 
#     print(user_text)
#     if user_text == "ㅋㅋ": # 만들기
#         await update.message.reply_text("왜웃냐")
#     elif user_text == "웃겨서": #웃겨서라고 보내면 뭐가웃기냐고 답장
#         await update.message.reply_text("뭐가웃기냐")

# async def handler(update, context):
#     user_text = update.message.text 
#     print(user_text)
    
#     if user_text == "비우기":
#         os.system('rm -rf ./temp/*')
#         await update.message.reply_text("임시 저장 폴더를 비웠습니다.")
#         return
    
#     if user_text == "이미지 전송 테스트":
#         # 이미지를 압축하지 않고 전송한다.
#         await update.message.reply_photo(photo=open('./temp/test.png', 'rb'))
#         return
    
#     site_name = ''
#     con_number = ''
    
#     is_success, site_name, con_number, con_title, msg = con_crawler.get_con_info(user_text)
    
    
async def help(update, context):
    msg = "사용법:"
    msg += "\n /help: 도움말을 출력합니다."
    msg += "\n /make: 콘만들기를 시작합니다."
    msg += "\n\t예시: /make arca 1234"
    msg += "\n\t사이트 이름: dc, arca"
    msg += "\n\n"
    msg += "\n dc콘은 아직 지원하지 않습니다."
    # msg += "\n /erase_temp: 임시 저장 폴더를 비웁니다."
    # msg += "\n이미지 전송 테스트: 이미지를 압축하지 않고 전송합니다."
    # context.message.reply_text(msg)
    await update.message.reply_text(msg)

async def erase_temp(update, context):
    os.system('rm -rf ./temp/*')
    await update.message.reply_text("임시 저장 폴더를 비웠습니다.")

async def make_con(update, context):

    try:
        site_name = context.args[0]
        con_number = context.args[1]
    except:
        msg = "사이트 이름과 콘 번호를 입력해주세요."
        msg += "\n예시: /make arca 1234"
        msg += "\n사이트 이름: dc, arca"
        await update.message.reply_text(msg)
        return
        
    msg = "콘만들기를 시작합니다."
    await update.message.reply_text(msg)
    
    is_success, site_name, con_number, con_title, msg = con_crawler.get_con_info(site_name + ' ' + con_number)
    
    if not is_success:
        await update.message.reply_text(msg)
        return
    
    # print(site_name), print(con_number), print(con_title)
    msg = '사이트 이름: ' + site_name
    msg += '\n콘 번호: ' + con_number
    msg += '\n콘 이름: ' + con_title
    await update.message.reply_text(msg)
    
    await update.message.reply_text("다운로드를 시작합니다.")
    
    if con_crawler.crawl_con(site_name, con_number):
        await update.message.reply_text("성공적으로 다운로드하였습니다.")
    else:
        await update.message.reply_text("사이트 이름을 잘못 입력하셨습니다.")
    
    await update.message.reply_text("업스케일링을 시작합니다.")
    if con_upscaler.upscale(site_name, con_number):
        await update.message.reply_text("성공적으로 업스케일링하였습니다.")
    else:
        await update.message.reply_text("업스케일링에 실패하였습니다.")
    
    await update.message.reply_text("콘을 100개씩 나눕니다.")
    con_crawler.divide_files(site_name, con_number)
    await update.message.reply_text("콘을 100개씩 나누었습니다.")
    
    bot_sign = ' by @parkings_stiker_bot 개인용 스티커 봇'
    
    await update.message.reply_text(f"{con_title}{bot_sign} 콘을 전송합니다.")


async def test_send_photo(update, context):
    # await update.message.reply_photo(photo=open('./test/test.png', 'rb'))
    await update.message.reply_document(document=open('./test/test.png', 'rb'))

async def test_send_video(update, context):
    await update.message.reply_video(video=open('./test/test.webm', 'rb'))
    
async def start(update, context):
    await update.message.reply_text("안녕하세요. 콘 만들기 봇입니다.")
    await update.message.reply_text("사용법은 /help를 입력해주세요.")

# 😂

print("핸들러 등록")
# echo_handler = MessageHandler(filters.ALL, handler)
help_handler = CommandHandler('help', help)
make_handler = CommandHandler('make', make_con)
test_send_photo_handler = CommandHandler('test_send_photo', test_send_photo)
test_send_video_handler = CommandHandler('test_send_video', test_send_video)

print("핸들러 등록")
# application.add_handler(echo_handler)
application.add_handler(help_handler)
application.add_handler(make_handler)
application.add_handler(test_send_photo_handler)
application.add_handler(test_send_video_handler)
print("핸들러 등록 완료")

print("application polling 시작")
application.run_polling()
