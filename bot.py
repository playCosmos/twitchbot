import sys
import irc.bot
import requests
import threading
import datetime
import codecs

#import urlfetch

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:' + token)], username, username)
        print('Connected to ' + server + ' on port ' + str(port) + '...')
        
    def on_welcome(self, c, e):
        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        print('mem ' + self.channel)
        c.cap('REQ', ':twitch.tv/tags')
        print('tags ' + self.channel)
        c.cap('REQ', ':twitch.tv/commands')
        print('coms ' + self.channel)
        c.join(self.channel)
        print('Joined ' + self.channel)

    def on_pubmsg(self, c, e):
        #print (e)

        filename = datetime.datetime.now()
        path = '/home/air/' + filename.strftime("%Y%m%d" + '.txt')
        f = open(path, 'a')
        try:
            f.write(e.tags[3]['value'] + ' : ' + e.arguments[0] + '\n')
        except:
            # 아마 utf-16으로 이모티콘이 들어와서 생기는 문제인듯
            f.write('!!!!\n')
            print ('!!!!')
            #c.privmsg(self.channel, '!!!')
        finally:
            f.close

        #print (e.tags[3]['value'] + ' : ' + e.arguments[0])
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]

            t=threading.Thread(target=self.do_command, args=(e, cmd))
            t.start()
            #self.do_command(e, cmd)
        return

    def do_command(self, e, cmd):
        c = self.connection

        # 게임.
        if cmd == "게임":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + '님은 현재 ' + r['game'] + ' 중 입니다.')

        # 방제
        elif cmd == "방제":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['status'])

        # 수온       
        elif cmd == "수온":
            url = 'http://hangang.dkserver.wo.tc'
            r = requests.get(url).json()
            c.privmsg(self.channel, r['time'] + '에 측정된 한강 수온은 ' + r['temp'] + '℃ 입니다.')

        #  팔로워
        elif cmd == '팔로워':
            url = 'https://api.twitch.tv/helix/users/follows?to_id=' + self.channel_id
            headers = {'Client-ID': self.client_id}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel,r['total'] + '명이 팔로우 중!')

        # 팔로우
        #elif cmd == "팔로우":
        #    following = requests.get('https://api.2g.be/twitch/followage/lah2/' + e.source.split('!')[0] +'?format=daysint')
        #    if following.text.find('is not following') >= 0:
        #        c.privmsg(self.channel, e.tags[3]['value'] + '님은 팔로우 하지 않았습니다.')
        #    else:
        #        c.privmsg(self.channel, e.tags[3]['value'] + '님과 만난지 ' + str(int(following.text)+1) + '일째')

        # 업타임
        #elif cmd == "업타임":
        #    url = ''
        
        # The command was not recognized
        #else:
        #    c.privmsg(self.channel, "Did not understand command: " + cmd)

def main():
    bot = TwitchBot(username, client_id, token, channel)
    bot.start()

if __name__ == "__main__":
    main()
