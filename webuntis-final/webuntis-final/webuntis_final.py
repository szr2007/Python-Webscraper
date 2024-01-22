
from email.policy import default
import time
import asyncio
from asyncio.windows_events import NULL
from cmath import exp
from decimal import ROUND_DOWN
import pyppeteer 
from multiprocessing.connection import wait
from pyppeteer import launch
import re
import json
from collections import defaultdict
import tkinter as tk

def display():
   window = tk.Tk()
   window.title("Lesson Grid")

   time_slots = range(800, 1800, 100)
   for i, time in enumerate(time_slots):
       tk.Label(window, text=f"{time}-{time + 100}", borderwidth=2, relief="raised").grid(row=i+1, column=0, sticky="nsew")
   window.mainloop()


async def login(url):
   await url.goto('https://melete.webuntis.com/WebUntis/?school=htl-donaustadt#/basic/login')

   await url.click('button[class="redesigned-button mt-1"]')

   with open("t.txt", "r") as f:
            username, password = f.read().split('/')

   await url.waitForSelector('#userNameInput')
   await url.type('#userNameInput', username);
   await url.click('span[class="next"]')

   await url.waitForSelector('#passwordInput')
   await url.type('#passwordInput', password)
   await url.click('span[class="submit submitPaginated"]')

   time.sleep(1)
   await url.waitForNavigation()

   


async def main():
   browserObj =await launch({
       "headless": False,
       })
   url = await browserObj.newPage()

   await login(url)


   await url.goto(f'https://melete.webuntis.com/WebUntis/api/public/timetable/weekly/data?elementType=5&elementId=3394&date=2023-10-13&formatId=1')
   url.waitForNavigation();
   time.sleep(1)

   json_data = await url.evaluate('''() => {
        return JSON.parse(document.querySelector("pre").textContent);
    }''')

   lesson_data = json_data["data"]["result"]["data"]["elementPeriods"]
   extended_lesson_data = json_data["data"]["result"]["data"]["elements"]

   lesson_grid = defaultdict(dict)
   for lesson_id, lesson_periods in lesson_data.items():
    for period in lesson_periods:
        date = period["date"]
        start_time = period["startTime"]
        end_time = period["endTime"]
        lesson_info = {
            "lessonId": lesson_id,
            "lessonCode": period["lessonCode"],
            "studentGroup": period.get("studentGroup", ""),
            "lessonState": period["cellState"],
            "elements": period["elements"],
            # Add more fields as needed
        }
        lesson_grid[date][start_time] = lesson_info


   unique_times = sorted(set(phase for phases in lesson_grid.values() for phase in phases.keys()))

   for date in sorted(lesson_grid.keys()):
    print(date, end="\n")
    for b in unique_times:
        lesson_info = lesson_grid[date].get(b, {})
        lesson_code = lesson_info.get("lessonCode", "")
        student_group = lesson_info.get("studentGroup", "")
        lesson_state = lesson_info.get("lessonState", "")
        lesson_elements = lesson_info.get("elements", "")
        ids = defaultdict(dict)
        for element in lesson_elements:
            ids[element.get("type", "")] = element.get("id", "")

        print(f"{lesson_code} ({student_group} - {lesson_state}; {ids[2]} {ids[4]})\t", end="\n")
    print("\n")

   await browserObj.close()

asyncio.get_event_loop().run_until_complete(main())


   #htmlContent = await url.content()
   #print(htmlContent)
   #await url.screenshot({'path': 'screenshot.png'})