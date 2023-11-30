import os
from PIL import Image
import ffmpeg

    
# .img 폴더에 있는 파일들을 4배 확대하여 img_4x 폴더에 저장, 512x512 크기로 img_512 폴더에 저장하는 함수
def upscale(site_name, con_number):
    CON_PATH = f'./temp/{site_name}_{con_number}'
    # ./{site_name}_{con_number}/img_4x 폴더가 없으면 생성한다.
    if not os.path.exists(f'{CON_PATH}/img_4x'):
        os.makedirs(f'{CON_PATH}/img_4x')
        
    # ./{site_name}_{con_number}/img_512 폴더가 없으면 생성한다.
    if not os.path.exists(f'{CON_PATH}/img_512'):
        os.makedirs(f'{CON_PATH}/img_512')
    total_num = len(os.listdir(f'{CON_PATH}/img'))
    now_num = 0
    
    
    for file_name in os.listdir(f'{CON_PATH}/img'):
        now_num += 1
        
        
        # .mp4 파일은 webm으로 변환한다.
        if file_name.endswith('.mp4'):
            mp4towebm(CON_PATH, file_name)
            continue
        
        # 512폴더에 이미지가 있으면 넘어간다.
        if os.path.exists(f'{CON_PATH}/img_512/' + file_name):
            print(str(now_num) + ' / ' + str(total_num) + ' 완료')
            continue
        
        # 4x        
        os.system(f'./waifu2x/waifu2x-ncnn-vulkan -i {CON_PATH}/img/' + file_name + f' -o {CON_PATH}/img_4x/' + file_name + ' -n 1 -s 4 -j 4:4:4 -f png -t auto -g -1')
        # 4x to 512x512
        img = Image.open(f'{CON_PATH}/img_4x/' + file_name)
        img = img.resize((512, 512))
        img.save(f'{CON_PATH}/img_512/' + file_name)
        
        print(str(now_num) + ' / ' + str(total_num) + ' 완료')
        
    # 완료될 경우 아래와 같은 메세지가 출력된다.
    print('Done')
    # img_4x 폴더를 삭제한다.
    os.system(f'rm -rf {CON_PATH}/img_4x')
    
    # 썸네일 생성
    # 첫 이미지 png 파일을 100x100으로 줄여 썸네일로 사용한다.
    for file_name in os.listdir(f'{CON_PATH}/img_512'):
        if file_name.endswith('.png'):
            img = Image.open(f'{CON_PATH}/img_512/' + file_name)
            img = img.resize((100, 100))
            img.save(f'{CON_PATH}/thumbnail.png')
            break
    
    # 비디오 썸네일 생성
    # 첫 비디오 파일을 webm으로 변환하여 썸네일로 사용한다.
    # 이미 변환된 파일이 있으면 넘어간다.
    if not os.path.exists(f'{CON_PATH}/thumbnail.webm'):
        for file_name in os.listdir(f'{CON_PATH}/img_512'):
            if file_name.endswith('.webm'):
                stream = ffmpeg.input(f'{CON_PATH}/img_512/' + file_name)
                stream = ffmpeg.output(stream, f'{CON_PATH}/thumbnail.webm', vcodec='libvpx-vp9', acodec='libopus', vf='scale=512:512', b='256K', an=None, r=60)
                ffmpeg.run(stream)
                break
    
    return True

# .mp4 파일을 webm으로 변환하는 함수
def mp4towebm(path, file_name):
    old_path = path + '/img/' + file_name
    new_path = path + '/img_512/' + file_name.replace('.mp4', '.webm')
    
    # 길이가 3초 이상인 파일은 넘어간다.
    probe = ffmpeg.probe(old_path)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    duration = float(video_stream['duration'])
    if duration > 3:
        return
    
    # # 용량이 256KB 이상인 파일은 넘어간다.
    # if os.path.getsize(old_path) > 256000:
    #     return
    
    # 이미 변환된 파일이 있으면 넘어간다.
    if os.path.exists(new_path):
        return
    
    # ffmpeg -i input.mp4 -c:v libvpx-vp9 -vf "scale:100x100" -b:a 128k -b:v 1M -c:a -an libopus output.webm
    # 프레임 60으로 고정
    stream = ffmpeg.input(old_path)
    stream = ffmpeg.output(stream, new_path, vcodec='libvpx-vp9', acodec='libopus', vf='scale=512:512', b='1M', an=None, r=60)
    ffmpeg.run(stream)
    