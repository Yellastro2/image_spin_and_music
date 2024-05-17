import gc
import os

from PIL import Image
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.VideoClip import ImageClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip

s_work_dir = 'frames/'

s_img_size = 300

try:
    os.mkdir(s_work_dir)
except:
    ok= 0

def crop_img2(f_imgpath):
    img = Image.open(f_imgpath)
    f_size = min(img.size)
    f_crop_size = (max(img.size))

    f_dif = int((f_crop_size - f_size) / 2)
    if img.height >= img.width:
        f_crop_img = img.crop((0,f_dif,img.width,img.height - f_dif))
    else:
        f_crop_img = img.crop((f_dif, 0, img.width - f_dif,img.height))

    return f_crop_img

def crop_img(f_imgpath,f_img_size = s_img_size):
    img = Image.open(f_imgpath)
    f_size = min(img.size)
    f_crop_size = (max(img.size))

    f_dif = int((f_crop_size - f_size) / 2)
    if img.height >= img.width:
        f_crop_img = img.crop((0,f_dif,img.width,img.height - f_dif))
    else:
        f_crop_img = img.crop((f_dif, 0, img.width - f_dif,img.height))

    # f_elips = int(f_size / 2)
    # f_elips_size = int(f_size / 20)
    #
    # draw = ImageDraw.Draw(f_crop_img)
    # draw.ellipse((f_elips - f_elips_size,
    #               f_elips - f_elips_size,
    #               f_elips + f_elips_size,
    #               f_elips + f_elips_size), fill="black")

    f_crop_img = f_crop_img.resize((f_img_size,f_img_size))

    return f_crop_img

# сохраняем каждый кадр в файл, возвращаем путь к файлу
def rotate(f_img,f_angle,f_result_path):
    f_res_path = f_result_path
    rotate_img = f_img.rotate(f_angle)
    rotate_img.save(f_result_path)
    return f_res_path


def rotate_set(f_img, f_speed,f_id):
    print('make rotate set')
    f_step = int(360 / f_speed)
    f_res = []
    # умножаем на минус потому что интуитивнее когда плюс крутит по часовой
    f_speed = -f_speed
    f_result_name = f_id
    for i in range(0, f_step):
        q_img = rotate(f_img, i * f_speed, f'{s_work_dir}{f_result_name}{i}_rotate.jpg')
        f_res.append(q_img)
        print(f'{i} in {f_step}')
    return f_res

def get_mask(f_name,f_size = s_img_size):
    f_path = f'mask_folder/{f_name}_{f_size}.png'
    if not os.path.exists(f_path):
        with Image.open(f'res/{f_name}') as og:
            with og.resize((f_size, f_size)) as rs:
                rs.save(f_path)

    return f_path

def spin_image(f_id = 0, f_len = 59, f_speed = 2, f_img = 'low.jpg',
               f_audio = "sneg.mp3", f_clb = None, f_mask = None,
               f_bitrate = '4000k',f_img_size = s_img_size,**kwargs):
    j = 0
    clips = []
    f_img_obj = crop_img(f_img,f_img_size)
    f_frames = rotate_set(f_img_obj,f_speed,f_id)
    f_img_obj.close()
    for i in range(0,f_len*24):
        print(f'append clips {i} in 60*24')
        clips.append(f_frames[j])
        j+= 1
        if j>= len(f_frames):
            j=0
    
    result_clip = ImageSequenceClip(clips,fps=24)

    logo = ImageClip(get_mask(f_mask,f_img_size),duration=result_clip.duration)
    f_mask = ImageClip(get_mask(f_mask,f_img_size),ismask=True).to_mask()
    logo = logo.set_mask(f_mask)
    result_clip = CompositeVideoClip([result_clip,logo])

    audio_clip = AudioFileClip(f_audio)
    if audio_clip.duration < result_clip.duration:
        f_count = int(result_clip.duration / audio_clip.duration) + 1
        f_clip_list = []
        for i in range(0,f_count):
            f_clip_list.append(audio_clip.copy().set_start(audio_clip.duration * i))
        f_clip_list[f_count - 1] = f_clip_list[f_count-1].copy().set_duration(result_clip.duration - ((f_count - 1) * audio_clip.duration))
        audio_clip = f_clip_list
    else:
        audio_clip = [audio_clip.set_duration(result_clip.duration)]
    new_audioclip = CompositeAudioClip(audio_clip)

    f_result_file = f'{s_files_path}{f_id}.mp4'
    print('set audio')
    result_clip.audio = new_audioclip


    print('set video')
    # libx264
    # mpeg4
    result_clip.write_videofile(f_result_file,
                                fps=24,
                                codec='libx264',
                                preset='medium',
                                bitrate=f_bitrate,
                                threads=2,
                                audio_bitrate='100k')

    audio_clip[0].close()
    new_audioclip.close()
    result_clip.close()
    f_result_name = f_id

    for i in range(0,len(f_frames)) :
        q_img = f'{s_work_dir}{f_result_name}{i}_rotate.jpg'
        os.remove(q_img)
    if f_clb:
        f_clb(f_result_file)
    if not f_audio == 'sneg.mp3':
        os.remove(f_audio)
    if not f_img == 'low.jpg':
        os.remove(f_img)
    gc.collect()
    return f_result_file
