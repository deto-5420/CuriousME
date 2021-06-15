from django.urls import path
from channels.routing import ProtocolTypeRouter, URLRouter, ChannelNameRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator

from collectanea.consumers import NotificationConsumer  # Importing notification Consumer from consumers.py
websockets=URLRouter([

    path("notifications/", NotificationConsumer),    # Url path for connecting to the websocket to send notifications.
    ])

application = ProtocolTypeRouter({ 
    # Websocket chat handler
    'websocket': websockets # Only allow socket connections from the Allowed hosts in the settings.py file
         # Session Authentication, required to use if we want to access the user details in the consumer 

})  