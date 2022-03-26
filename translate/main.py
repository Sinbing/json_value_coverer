import os
import json
import logging

# import configparser

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

# 需要 install的
import toml
import json5
import pyglet
from pyglet.window import key, mouse, Window

"""
总体思想：
把源文件的lang依次粘贴到新的lang里
"""

support_file_type = [".toml", ".json", ".json5"]


def load_file(file_path: str) -> dict or None:
    if not os.path.isfile(file_path):
        return None
    if not (file_type := os.path.splitext(file_path)[1]) in support_file_type:
        return None
    if file_type == ".toml":
        return toml.load(open(file_path, "r", encoding="utf-8"))
    elif file_type == ".json":
        return json.load(open(file_path, "r", encoding="utf-8"))
    elif file_type == ".json5":
        return json5.load(open(file_path, "r", encoding="utf-8"))


def paste_lang(src_key: dict, old_key: dict) -> tuple[dict, int]:
    # old_key: 旧版的翻译过的key (例如: zh_CN)
    # src_key: 新版的未翻译的key (例如: en_US)
    paste_count = 0
    out_lang = src_key.copy()
    for key, value in src_key.items():  # 依次遍历新版的lang
        if isinstance(value, dict):
            out_lang[key], paste_count_ = paste_lang(value, old_key[key])
            paste_count += paste_count_
            continue
        if key in old_key:  # 如果新版的key在旧版的key里
            out_lang[key] = old_key[key]
        else:  # 如果新版的key不在旧版的key里
            out_lang[key] = value
            paste_count += 1
    return out_lang, paste_count


def save_file(file_path: str, data: dict) -> bool:
    if not (file_type := os.path.splitext(file_path)[1]) in support_file_type:
        return False
    if file_type == ".toml":
        toml.dump(data, open(file_path, "w", encoding="utf-8"))
    elif file_type == ".json":
        json.dump(data, open(file_path, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    elif file_type == ".json5":
        json5.dump(data, open(file_path, "w", encoding="utf-8"), ensure_ascii=False, indent=4)
    return True


class ClientWindow(Window):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # logging
        self.logger = logging.getLogger('window')
        # batch
        self.button_batch = pyglet.graphics.Batch()
        self.label_batch = pyglet.graphics.Batch()
        # frame
        self.frame = pyglet.gui.Frame(self)
        # self.push_handlers(self.frame)
        # buttons
        self.buttons = {}
        self.setup_widget()
        self.src_lang = None
        self.old_lang = None
        self.out_path = None
        self.out_lang = {}

    def setup_widget(self):
        button_up = pyglet.image.load('./原始文件-1.png')
        button_down = pyglet.image.load('./原始文件-2.png')
        x = (self.width * 0.3) - (button_up.width / 2)
        self.buttons['old'] = pyglet.gui.ToggleButton(x=x, y=100,
                                                      depressed=button_up, pressed=button_down,
                                                      hover=button_up, batch=self.button_batch)
        self.buttons['old'].value = True
        self.buttons['old'].set_handler('on_toggle', self.old_button_press)
        self.frame.add_widget(self.buttons['old'])

        button_up = pyglet.image.load('./新版文件-1.png')
        button_down = pyglet.image.load('./新版文件-2.png')
        x = (self.width * 0.6) - (button_up.width / 2)
        self.buttons['new'] = pyglet.gui.ToggleButton(x=x, y=100,
                                                      depressed=button_up, pressed=button_down,
                                                      hover=button_up, batch=self.button_batch)
        self.buttons['new'].set_handler('on_toggle', self.new_button_press)
        self.frame.add_widget(self.buttons['new'])

        button_up = pyglet.image.load('./翻译-1.png')
        button_down = pyglet.image.load('./翻译-2.png')
        self.buttons['run'] = pyglet.gui.PushButton(x=300, y=150,
                                                    depressed=button_up, pressed=button_down,
                                                    hover=button_up, batch=self.button_batch)
        self.buttons['run'].set_handler('on_press', self.run_button_press)
        self.frame.add_widget(self.buttons['run'])

        # 淡蓝色的字
        self.text_label = pyglet.text.Label(text='退钱 啊啊啊啊！', font_name='fangsong', font_size=20,
                                            width=700, multiline=True, color=(0, 0, 255, 255),
                                            x=20, y=self.height - 100, batch=self.label_batch)

    """
    draws and some event
    """

    def on_draw(self, *dt):
        self.clear()
        self.draw_batch()

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height)

    def draw_batch(self):
        self.button_batch.draw()
        self.label_batch.draw()

    """
    button event
    """

    def new_button_press(self, pressed):
        self.logger.info(f'new button press {pressed}')
        self.buttons['old'].value = not pressed

    def old_button_press(self, pressed):
        self.logger.info(f'old button press {pressed}')
        self.buttons['new'].value = not pressed

    def run_button_press(self):
        self.logger.info(f'run button press')
        self.logger.info(f'目前的src_lang {self.src_lang}')
        self.logger.info(f'目前的old_lang {self.old_lang}')
        if (self.src_lang is None) or (self.old_lang is None):
            src = '' if self.src_lang is not None else ' 源文件'
            old = '' if self.old_lang is not None else '旧版文件 '
            self.text_label.text = f'请先选择{src} {old}!'
            return
        self.text_label.text = '转译中...'
        self.out_lang = paste_lang(self.src_lang, self.old_lang)
        self.text_label.text = f'转译完成!\n转译了 {self.out_lang[1]} 个key\n保存到 {self.out_path}'
        self.logger.info(f'out_lang: {self.out_lang}')
        save_file(self.out_path, self.out_lang[0])

    """
    keyboard and mouse input
    """

    def on_file_drop(self, x, y, paths):
        self.logger.info(f'file drop {paths}')
        if not os.path.splitext(paths[0])[1] in support_file_type:
            self.logger.error(f'file type not support {paths[0]}')
            self.text_label.text = f'文件类型不支持\n{paths[0]} !'
        try:
            lang = load_file(paths[0])
        except Exception as e:
            self.logger.error(f'load file error {e}')
            self.text_label.text = f'文件加载失败!\n{paths[0]}\n{e}'
            return
        if self.buttons['old'].value:  # 如果是旧版
            self.src_lang = lang
            self.text_label.text = f'旧版文件加载完毕\n{paths[0]} !'
        else:  # 如果是新版
            self.old_lang = load_file(paths[0])
            self.text_label.text = f'新版文件加载完毕\n{paths[0]} !'
            self.out_path = os.path.splitext(paths[0])[0] + '_new' + os.path.splitext(paths[0])[1]

    def on_mouse_motion(self, x, y, dx, dy) -> None:
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers) -> None:
        pass

    def on_mouse_press(self, x, y, button, modifiers) -> None:
        pass
        # self.logger.info(f'on_mouse_press {x}, {y}, {button}, {modifiers}')

    def on_mouse_release(self, x, y, button, modifiers) -> None:
        pass

    def on_key_press(self, symbol, modifiers) -> None:
        if symbol == key.ESCAPE and not (modifiers & ~(key.MOD_NUMLOCK |
                                                       key.MOD_CAPSLOCK |
                                                       key.MOD_SCROLLLOCK)):
            self.dispatch_event('on_close')

    def on_key_release(self, symbol, modifiers) -> None:
        pass

    def on_text_motion(self, motion):
        motion_string = key.motion_string(motion)

    def on_text_motion_select(self, motion):
        motion_string = key.motion_string(motion)

    def on_close(self, source: str = 'window') -> None:
        super().on_close()


main_window = ClientWindow(width=800, height=400,
                           caption="退钱！",
                           resizable=False,
                           file_drops=True,
                           visible=True, )

# 背景默认设置为白色
pyglet.gl.glClearColor(1, 1, 1, 1)

pyglet.app.run()
