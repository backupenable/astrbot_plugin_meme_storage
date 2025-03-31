from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api.message_components import Image
import astrbot.core.message.components as comp

import os
import pickle

import shutil
import random
# shutil.copyfile("source.txt", "destination.txt")


# 定义临时目录
PLUGIN_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(PLUGIN_DIR, "temp")
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

# 定义表情包字典文件
DATA_FILE = os.path.join(PLUGIN_DIR, "data.pkl")
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "wb") as f:
        pickle.dump({}, f)


@register("meme_storage", "backupenable", "存储并发送表情包", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.data = {}
        with open(DATA_FILE, "rb") as f:
            self.data = pickle.load(f)
        self.name = ""
        self.image_path = ""

    @filter.command("来只")
    async def send_meme(self, event: AstrMessageEvent, prompt: str):
        """
        从temp/prompt文件夹中随机抽取一张图片并发送，同时@发送者
        """
        meme_folder = os.path.join(os.path.dirname(__file__), "temp", prompt)

        if not os.path.exists(meme_folder):
            yield event.plain_result(f"{prompt} 不在白名单中")
            return

        image_files = [
            f
            for f in os.listdir(meme_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
        ]

        if not image_files:
            yield event.plain_result(f"{prompt}文件夹中没有图片")
            return

        random_image = random.choice(image_files)
        image_path = os.path.join(meme_folder, random_image)

        message_chain = [
            # At(qq=sender_id),
            Image.fromFileSystem(image_path)
        ]
        yield event.chain_result(message_chain)

    @filter.command("添加")
    async def add_meme(self, event: AstrMessageEvent):
        messages = event.get_messages()
        """
        引用消息的格式
        [Reply(type='Reply', id='775300007', chain=[Image(type='Image', file='DA41A9A99294120DD7558D5B108F3353.jpg', subType=1, url='https://multimedia.nt.qq.com.cn/download?appid=1407&fileid=EhTl1dNuW-1B5tddBZPWBDo_Wn31lxim9yAg_wool9zXkIy0jAMyBHByb2RQgL2jAVoQ7lyFop3kOyiOW25ZmhOABnoCYf8&spec=0&rkey=CAESKBkcro_MGujoEmz6gP4HRKIf_L37GbF7W1QSwB-My5aiM2_g1sflTJw', cache=True, id=40000, c=2, path='', file_unique='')], sender_id=3999504177, sender_nickname='luis', time=1743416535, message_str='', sender_str='', text='', qq=3999504177, seq=0), At(type='At', qq=3999504177, name='luis'), Plain(type='Plain', text=' \\添加 猫猫虫', convert=True)]
        """
        messages = event.get_messages()
        for _seg in messages:
            if isinstance(_seg, comp.Image):
                self.image_path = await _seg.convert_to_file_path()

            elif isinstance(_seg, comp.Plain):
                self.name = _seg.text.split()[1]
            elif isinstance(_seg, comp.Reply):
                self.image_path = await _seg.chain[0].convert_to_file_path()

        if self.name not in self.data:
            os.mkdir(os.path.join(TEMP_DIR, self.name))
            self.data[self.name] = 0
            with open(DATA_FILE, "wb") as f:
                pickle.dump(self.data, f)
        shutil.copyfile(
            self.image_path,
            os.path.join(
                TEMP_DIR, self.name, f"{self.data[self.name] + 1}{self.image_path[-4:]}"
            ),
        )
        self.data[self.name] += 1
        yield event.plain_result(f" 添加成功")

    async def terminate(self):
        """可选择实现 terminate 函数，当插件被卸载/停用时会调用。"""
        pass
