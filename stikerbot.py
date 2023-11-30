import pandas as pd
import telegram as tel
from telegram import Update
from telegram.ext import Updater, MessageHandler, CommandHandler
from telegram import StickerSet
from telegram.ext import filters
from telegram.ext import Application
import asyncio
import json
import aiogram

import os
import sys
import con_crawler, con_upscaler
import con_divide

import re

from random import randint, choice


df = pd.read_csv("./telegramapi.txt", sep=" ", header=None)

# api_token = df[1][0]
# chat_id = df[1][1]

API_TOKEN = df[1][0]
CHAT_ID = df[1][1]
JJAM_ID = df[1][2]

bot = tel.Bot(token=API_TOKEN)

BOT_NAME = df[1][6]
BOT_SIGN = df[1][7]
BOT_TITLE = df[1][8]

print("application 빌드")
application = Application.builder().token(API_TOKEN).build()
print("application 빌드 완료")
    
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
    
    await update.message.reply_text("콘을 50개씩 나눕니다.")
    con_divide.divide_files(site_name, con_number)
    await update.message.reply_text("콘을 50개씩 나누었습니다.")
    
    sticker_links = await make_sticker_pack(update, context, site_name, con_number, con_title)
    await update.message.reply_text("콘을 만들었습니다.")
    
    for sticker_link, sticker_title in sticker_links:
        await update.message.reply_text(f'{sticker_title} 스티커 팩을 만들었습니다.')
        await update.message.reply_text(f'{sticker_link}')
        
    await update.message.reply_text(f"{con_title} 스티커 완료.")
        
    
    

async def upload_files(update, context, site_name, con_number, con_title):
    # 패스 설정
    RESIZED_PATH = f'./temp/{site_name}_{con_number}'
    # anime_pack 폴더 패스
    anime_pack_path = f'{RESIZED_PATH}/anime_pack'
    # static 폴더 패스들
    static_folders = []
    for path in os.listdir(RESIZED_PATH):
        if path.startswith('static_'):
            static_folders.append(f'{RESIZED_PATH}/{path}')
    # static_folders = [f'{RESIZED_PATH}/static_' + str(i) for i in range(len(os.listdir(RESIZED_PATH)) - 4)] 
        
    # 썸네일 패스
    thumbnail_path = f'{RESIZED_PATH}/thumbnail.png'
    video_thumbnail_path = f'{RESIZED_PATH}/thumbnail.webm'
    
    await update.message.reply_text(f"{con_title}{BOT_TITLE} 콘을 업로드합니다.")
    
    # anime_pack 폴더에 있는 파일들을 모두 JJAM_ID에게 전송한다.
    # 없으면 넘어간다.
    anime_file_ids = None
    if os.path.exists(anime_pack_path):
        anime_file_ids = []
        for file_name in os.listdir(anime_pack_path):
            res = await bot.send_video(chat_id=JJAM_ID, video=open(anime_pack_path + '/' + file_name, 'rb'), supports_streaming=True)
            id = res.to_dict()['document']['file_id']
            anime_file_ids.append(id)
            
    await update.message.reply_text(f"{con_title}{BOT_TITLE} 움짤콘을 업로드하였습니다.")
        
    # static 폴더에 있는 파일들을 모두 JJAM_ID에게 전송한다.
    # 없으면 넘어간다.
    static_ids_list = []
    if len(static_folders) > 0:
        for static_folder in static_folders:
            static_file_ids = []
            for file_name in os.listdir(static_folder):
                res = await bot.send_document(chat_id=JJAM_ID, document=open(static_folder + '/' + file_name, 'rb'))
                id = res.to_dict()['document']['file_id']
                static_file_ids.append(id)
            static_ids_list.append(static_file_ids)
    
    await update.message.reply_text(f"{con_title}{BOT_TITLE} 스티커를 업로드하였습니다.")
    
    # 썸네일을 JJAM_ID에게 전송한다.
    res = await bot.send_document(chat_id=JJAM_ID, document=open(thumbnail_path, 'rb'))
    thumbnail_file_id = res.to_dict()['document']['file_id']
    # 비디오 썸네일을 JJAM_ID에게 전송한다.
    # 없으면 넘어간다.
    video_thumbnail_file_id = None
    if os.path.exists(video_thumbnail_path):
        res = await bot.send_document(chat_id=JJAM_ID, document=open(video_thumbnail_path, 'rb'))
        video_thumbnail_file_id = res.to_dict()['document']['file_id']
    
    await update.message.reply_text(f"{con_title}{BOT_TITLE} 썸네일을 업로드하였습니다.")
    
    return anime_file_ids, static_ids_list, thumbnail_file_id, video_thumbnail_file_id
        
    

async def make_sticker_pack(update, context, site_name, con_number, con_title):
    sticker_links = []
    
    emoji = '😂'
    
    anime_file_ids, static_ids_list, thumbnail_file_id, video_thumbnail_file_id = await upload_files(update, context, site_name, con_number, con_title)
    
    
    await update.message.reply_text(f"{con_title}{BOT_TITLE} 움짤 스티커 팩을 만듭니다.")
    # 움짤 스티커 팩 만들기
    # 없으면 넘어간다.
    if anime_file_ids != None:
        # 스티커 팩 이름
        sticker_pack_name = f'{site_name}_{con_number}_animated_{BOT_SIGN}'
        # 스티커 팩 타이틀
        sticker_pack_title = f'{con_title}_움짤_{BOT_TITLE}'
        # 스티커 형식
        sticker_pack_type = 'video'
        # 스티커들 배열
        stickers = []
        # 스티커들을 만든다.
        for anime_file_id in anime_file_ids:
            # sticker = aiogram.types.InputSticker(sticker=anime_file_id, emoji_list=[emoji])
            sticker = tel.InputSticker(sticker=anime_file_id, emoji_list=[emoji])
            # sticker = {
            #     'sticker' : anime_file_id,
            #     'emoji_list' : [emoji]
            # }
            # # 직렬화된 json 형태로 저장한다.
            # sticker = json.dumps(sticker)
            stickers.append(sticker)
        
        print(sticker_pack_name)
        print(sticker_pack_title)
        
        # 스티커 팩을 만든다.
        await bot.create_new_sticker_set(
            user_id=CHAT_ID,
            name=sticker_pack_name,
            title=sticker_pack_title,
            stickers=stickers,
            sticker_format=sticker_pack_type
        )
        # # 스티커 팩의 썸네일을 설정한다.
        # # 없으면 넘어간다.
        # if video_thumbnail_file_id != None:
        #     await bot.set_sticker_set_thumbnail(
        #         user_id=CHAT_ID,
        #         name=sticker_pack_name,
        #         thumbnail=video_thumbnail_file_id
        #     )
        
        sticker_links.append((f't.me/addstickers/{sticker_pack_name}', sticker_pack_title))
            
        # await update.message.reply_text(f'{sticker_pack_title} 스티커 팩을 만들었습니다.')
        # await update.message.reply_text(f't.me/addstickers/{sticker_pack_name}')
        
        print(f'{sticker_pack_title} 스티커 팩을 만들었습니다.')
        print(f't.me/addstickers/{sticker_pack_name}')
        
        await update.message.reply_text(f'{sticker_pack_title} 스티커 팩을 만들었습니다.')
        await update.message.reply_text(f't.me/addstickers/{sticker_pack_name}')
        
    # static 스티커 팩 만들기
    # 없으면 넘어간다.
    if len(static_ids_list) > 0:
        
        for static_ids, i in zip(static_ids_list, range(len(static_ids_list))):
            # 스티커 팩 이름
            sticker_pack_name = f'{site_name}_{con_number}_{i}_{BOT_SIGN}'
            # 스티커 팩 타이틀
            sticker_pack_title = f'{con_title}_{i}_{BOT_TITLE}'
            # 스티커 형식
            sticker_pack_type = 'static'
            # 스티커들 배열
            stickers = []
            # 스티커들을 만든다.
            for static_id in static_ids:
                # sticker = aiogram.types.InputSticker(sticker=static_id, emoji_list=[emoji])
                sticker = tel.InputSticker(sticker=static_id, emoji_list=[emoji])
                # sticker = {
                #     'sticker' : static_id,
                #     'emoji_list' : [emoji]
                # }
                # # 직렬화된 json 형태로 저장한다.
                # sticker = json.dumps(sticker)
                stickers.append(sticker)
            
            print(sticker_pack_name)
            print(sticker_pack_title)
            
            # 스티커 팩을 만든다.
            await bot.create_new_sticker_set(
                user_id=CHAT_ID,
                name=sticker_pack_name,
                title=sticker_pack_title,
                stickers=stickers,
                sticker_format=sticker_pack_type
            )
            # 스티커 팩의 썸네일을 설정한다.
            await bot.set_sticker_set_thumbnail(
                user_id=CHAT_ID,
                name=sticker_pack_name,
                thumbnail=thumbnail_file_id
            )
            
            # await update.message.reply_text(f'{sticker_pack_title} 스티커 팩을 만들었습니다.')
            # await update.message.reply_text(f't.me/addstickers/{sticker_pack_name}')
            
            print(f'{sticker_pack_title} 스티커 팩을 만들었습니다.')
            print(f't.me/addstickers/{sticker_pack_name}')
            
            await update.message.reply_text(f'{sticker_pack_title} 스티커 팩을 만들었습니다.')
            await update.message.reply_text(f't.me/addstickers/{sticker_pack_name}')
            
            sticker_links.append((f't.me/addstickers/{sticker_pack_name}', sticker_pack_title))
        
    return sticker_links
        
        
        
    
    
    
    
async def delete_sticker_pack(update, context):
    sticker_pack_name = context.args[0]
    await bot.delete_sticker_set(sticker_pack_name)
    await update.message.reply_text(f'{sticker_pack_name} 스티커 팩을 삭제하였습니다.')
    print(f'{sticker_pack_name} 스티커 팩을 삭제하였습니다.')
    
async def test_send_photo(update, context):
    # await update.message.reply_photo(photo=open('./test/test.png', 'rb'))
    # test_return = await update.message.reply_document(document=open('./test/test.png', 'rb'))
    test_return = await bot.send_document(chat_id=JJAM_ID, document=open('./test/test.png', 'rb'))
    print(test_return.to_dict()['document']['file_id'])

async def test_send_video(update, context):
    # test_return = await update.message.reply_video(video=open('./test/test.webm', 'rb'))
    test_return = await bot.send_video(chat_id=JJAM_ID, video=open('./test/test.webm', 'rb'))
    print(test_return.to_dict()['document']['file_id'])
    
async def start(update, context):
    await update.message.reply_text("안녕하세요. 개인용 아카디시콘 스티커 봇입니다.")
    await update.message.reply_text("사용법은 /help를 입력해주세요.")

# async def get_sticker_chat_test(update, context):
#     sticker_chat = update.set_
#     print(sticker_chat)

# 😂

print("핸들러 생성")
# echo_handler = MessageHandler(filters.ALL, handler)
help_handler = CommandHandler('help', help)
make_handler = CommandHandler('make', make_con)
test_send_photo_handler = CommandHandler('test_send_photo', test_send_photo)
test_send_video_handler = CommandHandler('test_send_video', test_send_video)
erase_temp_handler = CommandHandler('erase_temp', erase_temp)
start_handler = CommandHandler('start', start)
delete_handler = CommandHandler('delete_pack', delete_sticker_pack)
# get_sticker_chat_test_handler = CommandHandler('get_sticker_chat_test', get_sticker_chat_test)
print("핸들러 생성 완료")

print("핸들러 등록")
# application.add_handler(echo_handler)
application.add_handler(help_handler)
application.add_handler(make_handler)
application.add_handler(test_send_photo_handler)
application.add_handler(test_send_video_handler)
application.add_handler(erase_temp_handler)
application.add_handler(start_handler)
application.add_handler(delete_handler)
# application.add_handler(get_sticker_chat_test_handler)
print("핸들러 등록 완료")

print("application polling 시작")
application.run_polling()
