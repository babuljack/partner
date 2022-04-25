from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json  
from channels.db import database_sync_to_async
from .models import Message
from Account.models import User
class ChatConsumer(AsyncJsonWebsocketConsumer):


	@database_sync_to_async
	def create_chat(self, from_user, to_user, body):
		new_msg=Message.send_message(from_user, to_user, body)
		return new_msg

	async def connect(self):
		self.group_name=self.scope['user'].username
		await self.channel_layer.group_add(self.group_name,self.channel_name)
		await self.accept()
		
	async def receive_json(self,content,**kwargs):
			
			
			
			await self.send_json({
				"body":content,
				"recipient":self.group_name,
				})

			body=content
			fromU=self.scope['user']
			toU=self.scope['url_route']['kwargs']['chat_name']
			self.from_user=await database_sync_to_async(User.objects.get)(username=fromU)
			self.to_user=await database_sync_to_async(User.objects.get)(username=toU)
			new_msg =await self.create_chat(self.from_user,self.to_user,body)
			newbody=new_msg.body
			newrecipient=new_msg.user.username
			pic=json.dumps(new_msg.user.picture.url)
			data={
				   "body":newbody,
				   "recipient":newrecipient,
				   "picture":pic
				   }

			self.to_user_group=self.scope['url_route']['kwargs']['chat_name']
			await self.channel_layer.group_send(self.to_user_group,{
						'type':'chat.message',
						'message':data
				})

		 
	async def chat_message(self, event):
			message=event['message']
			await self.send_json(message)

			 


	async def disconnect(self,code):
		await self.channel_layer.group_discard(self.group_name,self.channel_name)

		