import datetime
import time
import requests
from flask import Flask,request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageAction,
    ButtonsTemplate, ImageCarouselTemplate, ImageCarouselColumn, URIAction,
    PostbackAction, DatetimePickerAction,
    CameraAction, CameraRollAction, LocationAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage, FileMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent,
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, SpacerComponent, IconComponent, ButtonComponent,
    SeparatorComponent, QuickReply, QuickReplyButton
)
 
app = Flask(__name__)
 
bot = LineBotApi('9h0Xgd1h790XxEmDh8J1FQVluo1IEzJyHZrZwAAnSwsei3gv8jL9IDztvJDdYeRL2uQgRFhKz41y6Q1dtTOjacT3kS53LKJn+FYhDlgluNr7SbAlR7gJLncS5XZtoXimOTRDiyvygFM5+mfXs4HKtAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('8d47cc5dafc17f6ff361f4b3990c4b62')

@app.route("/") 
def index():
    return "Bot running"

@app.route("/callback",methods=['POST']) 
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
 
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
 
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent,message=TextMessage)
def handle_text_message(event):
    url_add = 'http://botworks.rf.gd/add_task.php?'
    asg = []
    fltr = []
    tempList = ""
    fltrAsg = ""
    key = 0
    idx = 0
    msg = event.message.text
       
    if msg.startswith("+_"):
        user_id = event.source.user_id
        profile = bot.get_profile(user_id)
        fltr = msg.split("_")
        if len(fltr) > 2:
            bot.reply_message(event.reply_token,TextSendMessage(text="Masukan formatnya dengan benar ya kak " + profile.display_name +"! :)"))
        else:
            data = fltr[1].split("|")
            name = data[0]
            course = data[1]
            try:
                tempDate = data[2].split("/")
                if len(tempDate[2]) < 4:
                    raise ValueError('Tahun salah')
                tempDate = list(map(int,tempDate))
            except ValueError:
                bot.reply_message(event.reply_token,TextSendMessage(text="Masukan format tanggal dengan benar ya kak " + profile.display_name +"! :)"))

            date = datetime.datetime(tempDate[2], tempDate[1], tempDate[0], tempDate[3], tempDate[4])
            date = date.strftime('%Y-%m-%d %H:%M')
            payload = 'name={}&crs={}&dl={}'.format(name, course, date)
            send = requests.get(url_add+payload)
            if send.status_code == 200:
                bot.reply_message(event.reply_token,TextSendMessage(text="Tugas berhasil di tambahkan. Terimakasih kak " + profile.display_name +"! :)"))
            else:
                bot.reply_message(event.reply_token,TextSendMessage(text="Maaf! Sepertinya terjadi kendala pada server!"))

    elif msg.lower() == "help":
        imagecarousel_reply = TemplateSendMessage(
            alt_text='Help command',
            template=ImageCarouselTemplate(
                columns=[
                    ImageCarouselColumn(
                        image_url='https://i.imgur.com/ZBXhDv2.jpg',
                        action=PostbackAction(
                            data="help"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://i.imgur.com/jlhKYFI.jpg',
                        action=PostbackAction(
                            data="cmd"
                        )
                    ),
                    ImageCarouselColumn(
                        image_url='https://i.imgur.com/ky4UCFb.jpg',
                        action=PostbackAction(
                            data="cntcus"
                        )
                    )
                ]
            )
        )
        bot.reply_message(event.reply_token, imagecarousel_reply)
    elif msg.lower() == "clear list":
        if delAsg == "":
            bot.reply_message(event.reply_token,TextSendMessage(text="Belum ada list ditambahkan!"))
        else:
            tsAuth = time.time()
            confirm_clearlist= TemplateSendMessage(
                alt_text='Konfirmasi Clear list.',
                template=ConfirmTemplate(
                    text='Apakah kamu yakin ingin menghapus list?',
                    actions=[
                        PostbackAction(label="Ya", data="yes&{}".format(tsAuth)),
                        PostbackAction(label="Tidak", data="no&{}".format(tsAuth))
                    ]
                )
            )
            bot.reply_message(event.reply_token,confirm_clearlist)
    elif msg.lower() == "tugas terdekat":
        if tempAsg == "":
            bot.reply_message(event.reply_token,TextSendMessage(text="Belum ada tugas ditambahkan, coba tambahin dulu kak :)"))
        else:
            with open('Deadlinemaster', 'r') as f:
                asg = f.readlines()

            tempFltr = "20-12-3019 00:00"
            dateFltr = datetime.datetime.strptime(tempFltr, '%d-%m-%Y %H:%M')
            for x in range(len(asg)):
                data = asg[x].split("|")
                fltrDate = data[2]
                asgDate = datetime.datetime.strptime(fltrDate[:-1], '%d-%m-%Y %H:%M')
                if asgDate < dateFltr:
                    dateFltr = asgDate
                    idx = x
            data = asg[idx].split("|")
            tempList += "Tugas: {}\nMata Kuliah: {}\nDeadline: {}\n".format(data[0], data[1], data[2])
            tempList += "Jangan lupa kerjain ya!"
            bot.reply_message(event.reply_token,TextSendMessage(text=tempList))
    elif msg.startswith("Del_") or msg.startswith("del_"):
        asgName = msg.split("_")
        for x in range(len(asg)):
            data = asg[x].split("|")
            if asgName[1] in data[0]:
                key = 1
                continue
            else:
                fltrAsg += "{}|{}|{}".format(data[0],data[1],data[2])

        if key == 0:
            bot.reply_message(event.reply_token,TextSendMessage(text="Maaf kak, tidak ada tugas yang namanya '" + asgName[1] + "'"))
        else:
            bot.reply_message(event.reply_token,TextSendMessage(text="Tugas '" + asgName[1] +"' berhasil dihapus!"))
    elif msg.lower() == "list tugas":
        if tempAsg == "":
            bot.reply_message(event.reply_token,TextSendMessage(text="Belum ada tugas nih kak"))
        else:
            with open('Deadlinemaster', 'r') as f:
                asg = f.readlines()
            for x in range(len(asg)):
                data = asg[x].split("|")
                fltrDate = data[2]
                fltrDate = datetime.datetime.strptime(fltrDate[:-1], '%d-%m-%Y %H:%M')
                today = str((datetime.datetime.now() + datetime.timedelta(0,0,0,0,0,7,0)).strftime('%d-%m-%Y %H:%M'))
                today = datetime.datetime.strptime(today, '%d-%m-%Y %H:%M')
                if today <= fltrDate:
                    fltrAsg += "{}|{}|{}".format(data[0],data[1],data[2])
                    tempList += "Tugas: {}\nMata Kuliah: {}\nDeadline: {}\n".format(data[0], data[1], data[2])
            tempList += "Jangan lupa kerjain ya!"

            f = open("Deadlinemaster", "w")
            f.write(fltrAsg)
            f.close()

            if(tempList == "Jangan lupa kerjain ya!"):
                bot.reply_message(event.reply_token,TextSendMessage(text="Deadline tugas sudah lewat, kamu bisa tambahkan tugas baru! :)"))
            else:
                bot.reply_message(event.reply_token,TextSendMessage(text=tempList))
    elif msg.lower() == "/bot reset":
        user_id = event.source.user_id
        group_id = event.source.group_id
        if user_id == "U5be5a4d34b14f559c151d29595a983ab":
            bot.reply_message(event.reply_token,TextSendMessage(text="[Admin Confirmed] Please wait!"))
            time.sleep(3)
            bot.push_message(group_id, TextSendMessage(text='Sending request to server..'))
            time.sleep(1)
            bot.push_message(group_id, TextSendMessage(text='Bot has been reset!'))
            f = open("Tokenlist", "w")
            f.write("")
            f.close()
        else:
            bot.reply_message(event.reply_token,TextSendMessage(text="Maaf kak, command ini hanya dapat digunakan oleh admin."))


@handler.add(PostbackEvent)
def handle_postback(event):
    server = ftplib.FTP()
    server.connect('ftpupload.net', 21)
    server.login('epiz_23534805','2BXJ2CNU3Y')
    token = str(event.postback.data).split("&")
    match = 0
    with open('Tokenlist', 'r') as f:
        tokenList = f.readlines()
    if tokenList != "":
        for x in range(len(tokenList)):
            if token[1] == str(tokenList[x][:-1]):
                match = 1

    if token[0] == "yes":
        if match != 1:
            bot.reply_message(event.reply_token, TextSendMessage(text='Okay, list berhasil dihapus!'))
            f = open("Deadlinemaster", "w")
            f.write("")
            f.close()
    elif token[0] == "no":
        if match != 1:
            bot.reply_message(event.reply_token, TextSendMessage(text='Baiklah, hapus list dibatalkan!'))

if __name__ == "__main__":
    app.run()