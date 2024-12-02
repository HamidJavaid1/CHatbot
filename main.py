import asyncio
import pyttsx3
import google.generativeai as genai
from flet import *
import dotenv
import os

dotenv.find_dotenv()

# pyttsx3.speak("Hey I am your chatbot, tell me how can I assist you")
genai.configure(api_key = os.getenv('API_KEY'))
model = genai.GenerativeModel("gemini-1.5-flash-002")

class MainChatbot(Column):
    def __init__(self,page):
        super().__init__()
        self.page = page
        self.scroll = ScrollMode.ALWAYS
        self.expand = True
        self.auto_scroll = True
        self.horizontal_alignment = CrossAxisAlignment.CENTER

        # Chat container to display messages
        self.chatcontainer = Column(horizontal_alignment=CrossAxisAlignment.CENTER, expand=True)
        self.controls.append(self.chatcontainer)

        # Create the Enter button
        self.enterbtn = ElevatedButton(
            icon=Icons.ARROW_FORWARD_OUTLINED,
            text="Enter",
            on_click=self.entersubmit,
        )

        # TextField for user input
        self.promptvalue = TextField(
            value="Enter your prompt here...",
            on_click=self.removeplaceholder,
            height=50,
            width=500,
            border="4",
            suffix=self.enterbtn,
            on_submit=self.entersubmit,
            border_radius=10,
            border_color="#36618E"
        )

        # Container to hold the TextField at the bottom
        self.textcontainer = Container(
            alignment=alignment.bottom_center,
            content=self.promptvalue,
            expand=True,
            padding=padding.only(top=200,bottom=60),
        )

        # Add the text container to the bottom
        self.controls.append(self.textcontainer)

    async def fetch_response(self, userrequest):
        """Asynchronous method to fetch response."""
        await asyncio.sleep(0.1)  # Simulate a slight delay for demonstration
        return model.generate_content(userrequest)

    def entersubmit(self, e):
        # Get user input
        userrequest = self.promptvalue.value

        # Display loading indicator
        loading_indicator = Container(
        content=ProgressRing(width=16, height=16, stroke_width=3),
        alignment=alignment.center,
        
        expand=True,
        padding=padding.only(top=60,bottom=60),
    )
        
        self.chatcontainer.controls.insert(0, loading_indicator)
        self.update()

        async def handle_response():
            try:
                # Fetch response asynchronously
                chatresponse = await self.fetch_response(userrequest)
            finally:
                # Remove loading indicator
                self.chatcontainer.controls.remove(loading_indicator)
                self.update()

            self.chatcoulmn = Column(horizontal_alignment=CrossAxisAlignment.CENTER)
            user_message = Text(userrequest, size=16 , weight="bold",)
            bot_message = Text(chatresponse.text, size=16, style=TextStyle.italic)
            self.speakbotbtn = ElevatedButton(icon=Icons.AUDIO_FILE_OUTLINED, text="Listen chat", on_click= lambda e, speak=bot_message.value:self.handlespeak(speak))
            spkbtncontainer = Container(alignment=alignment.bottom_right, content=self.speakbotbtn , expand=True)
                # Append new messages to the chat containe
            self.chatcoulmn.controls.insert(0, spkbtncontainer,)
            self.chatcoulmn.controls.insert(0, bot_message)  # Insert response
            self.chatcoulmn.controls.insert(0, user_message)

# Chat UI container
            self.chatui = Container(
                content=self.chatcoulmn,
                margin=20,
                padding=10,
                width=800,
         #       shadow=[
       # BoxShadow(
        #    color="rgba(0, 0, 0, 0.1)",  # Shadow color
         #   blur_radius=10,  # How blurry the shadow is
          #  offset=Offset(0.1,0)
        #)
    #],
            )    


            self.chatcontainer.controls.append(self.chatui)  # Insert user input

            # Clear the prompt field after submission
            self.promptvalue.value = "Enter your prompt here..."
            self.update()

        # Start handling the response asynchronously
        asyncio.run(handle_response())
    def removeplaceholder(self,e):
        if self.promptvalue.value == "Enter your prompt here...":
            self.promptvalue.value = None
            self.update()
        else:
            self.promptvalue.value = self.promptvalue.value
            self.update()
    def handlespeak(self, whattospeak):
    # Initialize pyttsx3 engine
        self.engine = pyttsx3.init()

        # Start speaking the text
        self.engine.say(whattospeak)
        
        # Change button to "Stop" during speech
        self.speakbotbtn.text = "Stop"
        self.speakbotbtn.icon = Icons.STOP
        
        # Change the button action to stop the speech when clicked
        self.speakbotbtn.on_click = lambda e: self.stop_speech()  # Handle stop action
        self.update()

        # Define a callback after the speech is completed
        def on_speech_done(name, completed):
            if completed:
                # Once speech is done, revert the button back to "Listen chat"
                self.reset_speak_button(whattospeak)

        # Register callback for speech completion
        self.engine.connect('finished-utterance', on_speech_done)
        
        # Run the speech engine
        self.engine.runAndWait()

    def stop_speech(self):
        # Stop the speech manually and revert button
        self.engine.stop()
        
        # Revert button text and icon
        self.reset_speak_button(self.speakbotbtn.text)  # Use current text as input for handlespeak
        self.update()

    def reset_speak_button(self, whattospeak):
        # Reset the button to "Listen chat" and setup it for re-triggering speech
        self.speakbotbtn.text = "Listen chat"
        self.speakbotbtn.icon = Icons.AUDIO_FILE_OUTLINED
        self.speakbotbtn.on_click = lambda e, speak=whattospeak: self.handlespeak(speak)  # Reset to original function
        self.update()



       
def main(page: Page):
    page.title = "Chatbot"
    page.vertical_alignment = MainAxisAlignment.CENTER
    page.horizontal_alignment = CrossAxisAlignment.CENTER
    
    def changebackground(e):
        if nav.actions[0].icon == icons.WB_SUNNY_OUTLINED:
            nav.actions[0].icon = icons.DARK_MODE
            page.theme_mode = ThemeMode.DARK
        else:
            nav.actions[0].icon = icons.WB_SUNNY_OUTLINED
            page.theme_mode = ThemeMode.LIGHT
        page.update()

    # Navigation bar
    nav = AppBar(
        leading=Icon(icons.CHAT_BUBBLE),
        leading_width=40,
        title=Text("MY CHAT BOT"),
        center_title=True,
        bgcolor=colors.SURFACE_VARIANT,
        actions=[
            IconButton(icons.WB_SUNNY_OUTLINED , on_click=changebackground),
            IconButton(icons.FILTER_3),
            PopupMenuButton(
                items=[
                    PopupMenuItem(text="Item 1"),
                    PopupMenuItem(),  # divider
                    PopupMenuItem(text="Checked item", checked=False),
                ]
            ),
        ],
    )

    # Add the navigation bar and the chatbot container to the page
    mainbot = MainChatbot(page)
    page.add(nav, mainbot)


app(target=main)
