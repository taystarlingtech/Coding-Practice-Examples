import pyautogui
import time
pyautogui.FAILSAFE = False
while True:
    time.sleep(15)
    for i in (0, 100):
        pyautogui.moveTo(0, i+5)
    for i in range(0, 3):
        pyautogui.press('shift')

#I've messed with all the power and sleep settings, but my computer still goes to sleep.
#When it does, it becomes completely unresponsive to keyboard and mouse input. I have to power it off and back on again.
#Meaning I have to re-sign and 2fa in everywhere again. It's a pain and I might forget a program. 
#The intention of this program is to make my work life easier, and not to avoid responsibility. That's all.