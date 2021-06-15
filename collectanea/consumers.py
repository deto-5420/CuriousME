from channels.generic.websocket import AsyncJsonWebsocketConsumer

import json
from asgiref.sync import async_to_sync,sync_to_async
import asyncio
from rest_framework.authtoken.models import Token
@sync_to_async
def getusers(token):
    obj=Token.objects.filter(key=token).first()
    if not obj :
        return None 
    else:
        return obj.user.id
class NotificationConsumer(AsyncJsonWebsocketConsumer):

    # async def connect(self):
    #     await self.accept()
    #     await self.channel_layer.group_add("", self.channel_name)
    #     print(f"Added {self.channel_name} channel to gossip")

    # async def disconnect(self, close_code):
    #     await self.channel_layer.group_discard("gossip", self.channel_name)
    #     print(f"Removed {self.channel_name} channel to gossip")
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        try:
            # Pass auth token as a part of url.
            # print(self.scope.get('query_string'))
            token = self.scope.get('query_string').decode("utf-8")
            # print(token)
            # print("HI")
            # If no token specified, close the connection
            if not token:
                print(1)
                await self.close()
            # Try to authenticate the token from DRF's Token model
            print("HI")
            try:
                print("H")
                obj = await getusers(token)
                if obj:
                    print("token verified")
                else:
                    await self.close()
            except Exception as E:
                print(str(E),1)
                await self.close()


            
            group_name = str(obj)
            print(group_name)
            # Add this channel to the group.

            await self.channel_layer.group_add(
                group_name,
                self.channel_name,
            )
            await self.accept()

        except Exception as e:
            print(str(e))
            await self.close()

    async def disconnect(self, code):
        """
        Called when the websocket closes for any reason.
        Leave all the rooms we are still in.
        """
        try:
            # Get auth token from url.
            token = self.scope.get('query_string').decode("utf-8")
            try:
                print("H")
                obj = await getusers(token)
                
            except Exception as E:
                print(str(E),1)
                await self.close()
            # Get the group from which user is to be kicked.
            group_name = str(obj)

            # kick this channel from the group.
            await self.channel_layer.group_discard(group_name, self.channel_name)
        except Exception as e:
            pass

    async def user_like(self, event):
        await self.send_json(event)
        print(f"Got message {event} at {self.channel_name}")
    async def user_reply(self, event):
        await self.send_json(event)
        print(f"Got message {event} at {self.channel_name}")
    async def user_answerlike(self, event):
        print("hey")
        await self.send_json(event)
        print(f"Got message {event} at {self.channel_name}")
# class NotificationConsumer(AsyncJsonWebsocketConsumer):
#     # Function to connect to the websocket
#     async def connect(self):
#         await self.accept()
#         while 1:
#             await asyncio.sleep(1)
#             await self.send_json("tick")
#             await asyncio.sleep(1)
#             await self.send_json(".....tock")
    # def connect(self):
    #    # Checking if the User is logged in
    #     if self.scope["user"].is_anonymous:
    #         # Reject the connection
    #         self.close()
    #     else:
    #         # print(self.scope["user"])   # Can access logged in user details by using self.scope.user, Can only be used if AuthMiddlewareStack is used in the routing.py
    #         self.group_name = str(self.scope["user"].pk)  # Setting the group name as the pk of the user primary key as it is unique to each user. The group name is used to communicate with the user.
    #         async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
    #         self.accept()

    # # Function to disconnet the Socket
    # def disconnect(self, close_code):
    #     self.close()
    #     # pass

    # # Custom Notify Function which can be called from Views or api to send message to the frontend
    # def notify(self, event):
    #     self.send(text_data=json.dumps(event["text"]))