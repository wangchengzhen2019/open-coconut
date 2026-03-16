

from microbit import *
import random

# 自定义图片：你的 micro: bit 图标（5x5 LED 点阵）
MICROBIT_ICON = Image(
    "09990:"
    "90009:"
    "90909:"
    "90009:"
    "09990"
)

# 笑脸 / 哭脸图标
HAPPY = Image.HAPPY
SAD = Image.SAD

def show_random_icon():
"""随机显示图标"""
icons = [MICROBIT_ICON, HAPPY, SAD]
display.show(random.choice(icons))

def scroll_text(text: str, delay: int = 150):
"""滚动显示文本"""
display.scroll(text, delay = delay)

def sensor_interaction():
"""传感器交互：根据光线/按钮切换显示"""
while True:
        # 按钮 A：显示自定义图标
if button_a.was_pressed():
    display.show(MICROBIT_ICON)
sleep(1000)
        
        # 按钮 B：滚动文本
if button_b.was_pressed():
    scroll_text("I ❤️ micro:bit")
        
        # 光线传感器：暗的时候显示笑脸
light = display.read_light_level()
if light < 50:
    display.show(HAPPY)
else:
display.clear()

sleep(100)

if __name__ == "__main__":
    # 开机动画：显示 micro: bit 图标
display.show(MICROBIT_ICON)
sleep(2000)
scroll_text("HELLO")
sensor_interaction()
