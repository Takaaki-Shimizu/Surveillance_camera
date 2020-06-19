import datetime
import numpy as np
import subprocess
import os
import cv2
import time
import requests

token = '' 

last_post = datetime.datetime(2000, 1, 1) # 適当に初期化
# 保存パスの指定
save_path = "./"
def main():
    # カメラのキャプチャを開始
    cam = cv2.VideoCapture(0)
    # フレームの初期化 --- (*1)
    img1 = img2 = img3 = get_image(cam)
    motion_th = 300
    while True:
        #時刻取得
        time = datetime.datetime.now()
        strtime = time.strftime('%Y%m%d_%H-%M-%S')
        FileName = strtime + ".jpg"

        # Enterキーが押されたら終了
        if cv2.waitKey(1) == 13: break
        # 差分を調べる --- (*2)
        diff = check_image(img1, img2, img3)
        # 差分がmotion_thの値以上なら動きがあったと判定 --- (*3)
        motion = cv2.countNonZero(diff)
        if motion > motion_th:
        # 写真を撮影 --- (*4)
            cv2.imwrite(FileName,img3)
            print("カメラに動きを検出")

            payload = {'message': '不審物感知しました'}  # 送信メッセージ
            url = 'https://notify-api.line.me/api/notify'
            headers = {'Authorization': 'Bearer ' + token}

            files={"imageFile":open(FileName,"rb")}
            res = requests.post(url, data=payload, headers=headers,files=files,)  # LINE NotifyへPOST
            print(res)

            cv2.imshow('PUSH ENTER KEY', img3)

        else:
            pass
        # 比較用の画像を保存 --- (*5)
        img1, img2, img3 = (img2, img3, get_image(cam))
    # 後始末
    cam.release()
    cv2.destroyAllWindows() 

# 画像に動きがあったか調べる関数
def check_image(img1, img2, img3):
    # グレイスケール画像に変換 --- (*6)
    gray1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY)
    gray3 = cv2.cvtColor(img3, cv2.COLOR_RGB2GRAY)
    # 絶対差分を調べる --- (*7)
    diff1 = cv2.absdiff(gray1, gray2)
    diff2 = cv2.absdiff(gray2, gray3)
    # 論理積を調べる --- (*8)
    diff_and = cv2.bitwise_and(diff1, diff2)
    # 白黒二値化 --- (*9)
    _, diff_wb = cv2.threshold(diff_and, 30, 255, cv2.THRESH_BINARY)
    # ノイズの除去 --- (*10)
    diff = cv2.medianBlur(diff_wb, 5)
    return diff

# カメラから画像を取得する
def get_image(cam):
    img = cam.read()[1]
    img = cv2.resize(img, (600, 400))
    return img
main()