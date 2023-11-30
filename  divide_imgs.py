import os

# imgs_512 폴더에 있는 파일중 .webm 파일을 찾아 anime_pack 폴더에 저장한다.
# 나머지 png 파일은 100개씩 나누어 static_0, static_1, static_2, ... 폴더에 저장한다.
def divide_files(site_name, con_number):
    resized_path = f'./temp/{site_name}_{con_number}/img_512'
    
    # .webm 파일이 있는지 확인한다.
    webm_files = [file_name for file_name in os.listdir(resized_path) if file_name.endswith('.webm')]
    # .webm 파일이 있으면 anime_pack 폴더에 저장한다.
    if len(webm_files) > 0:
        # anime_pack 폴더가 있을 경우 삭제한다.
        if os.path.exists('./anime_pack'):
            os.system('rm -rf ./anime_pack')
        # anime_pack 폴더를 생성한다.
        os.makedirs('./anime_pack')
        # anime_pack 폴더에 .webm 파일을 저장한다.
        for file_name in webm_files:
            os.system(f'cp {resized_path}/{file_name} ./anime_pack')
        
    # .png 파일이 있는지 확인한다.
    png_files = [file_name for file_name in os.listdir(resized_path) if file_name.endswith('.png')]
    # 필요한 static 폴더의 개수를 구한다.
    static_num = len(png_files) // 100 + 1

    for i in range(static_num):
        # static 폴더가 있을 경우 삭제한다.
        if os.path.exists(f'./static_{i}'):
            os.system(f'rm -rf ./static_{i}')
        # static 폴더를 생성한다.
        os.makedirs(f'./static_{i}')
            
    # static 폴더에 .png 파일을 저장한다.
    for i in range(static_num):
        for file_name in png_files[i*100:(i+1)*100]:
            os.system(f'cp {resized_path}/{file_name} ./static_{i}')