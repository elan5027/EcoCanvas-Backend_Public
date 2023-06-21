from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from users.models import User
from .models import ShopProduct
import json


class RestockConsumer(WebsocketConsumer):
    '''
    작성자 : 장소은
    내용 : 웹소켓 연결, notification_group의 모든 컨슈머에게 메세지 보내기 
    최초 작성일: 2023.06.21
    '''

    def connect(self):
        # notification_group 그룹에 컨슈머 추가(알림 메세지 수신),
        async_to_sync(self.channel_layer.group_add)(
            "notification_group", self.channel_name)
        self.accept()  # 웹 소켓 연결 수락
        self.send(text_data=json.dumps({'message': '연결 테스트'}))

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            "notification_group", self.channel_name)

    def receive(self, text_data):
        pass

    def notification_message(self, event):
        message = event['message']
        self.send(text_data=message)
