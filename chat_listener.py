import json
import subprocess

from twitchio.ext import commands


with open('secret.json', 'r') as f:
    data = json.load(f)
    token = data['token']
    channel = data['channel']
    reward_id = data['reward-id']


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(token=token, prefix='!', initial_channels=[channel])

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'Connected to channel | {channel}')

    async def event_message(self, message):
        if 'custom-reward-id' in message.tags:
            if message.tags['custom-reward-id'] == reward_id:
                try:
                    i = int(message.content)
                    if 1 <= i <= 151:
                        subprocess.run(['.venv/Scripts/python.exe', 'main.py', str(i)])
                        return
                except Exception as e:
                    await message.channel.send(e.args[0])

                await message.channel.send('Nur Zahlen von 1 bis 151!')

        # Ensure the bot ignores its own messages
        if message.author.name.lower() == self.nick.lower():
            return


bot = Bot()
bot.run()
