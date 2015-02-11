#!/usr/bin/python2
'''

@author: Shaun Amarelo
	
This is a Hack and extension of original script offered by:

	@author: Jeremy Blythe
	Motion Uploader - uploads videos to Google Drive
	Read the blog entry at http://jeremyblythe.blogspot.com for more information
'''

import smtplib
from datetime import datetime

import os.path
import sys

import gdata.data
import gdata.docs.data
import gdata.docs.client
import ConfigParser

class MotionUploader:
    def __init__(self, config_file_path):
        # Load config
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file_path)
        
        # GMail account credentials
        self.username = self.config.get('gmail', 'user')
        self.password = self.config.get('gmail', 'password')
        self.from_name = self.config.get('gmail', 'name')
        self.sender = self.config.get('gmail', 'sender')
        
        # Recipient email address (could be same as from_addr)
        self.recipient = self.config.get('gmail', 'recipient')        
        
        # Subject line for email
        #self.subject = config.get('gmail', 'subject')
        
        # First line of email message
        #self.message = self.config.get('messages', 'video')
                
        # Folder (or collection) in Docs where you want the videos to go
        self.folder = self.config.get('docs', 'folder')
        
        # Options
        self.delete_after_upload = self.config.getboolean('options', 'delete-after-upload')
        self.send_email = self.config.getboolean('options', 'send-email')
        
        self._create_gdata_client()
		
    def _create_gdata_client(self):
        """Create a Documents List Client."""
        self.client = gdata.docs.client.DocsClient(source='motion_uploader')
        self.client.http_client.debug = False
        self.client.client_login(self.username, self.password, service=self.client.auth_service, source=self.client.source)
               
    def _get_folder_resource(self):
        """Find and return the resource whose title matches the given folder."""
        col = None
        for resource in self.client.GetAllResources(uri='/feeds/default/private/full/-/folder'):
            if resource.title.text == self.folder:
                col = resource
                break    
        return col
    
    def _send_email(self,msg,reason):
        '''Send an email using the GMail account.'''
        senddate=datetime.strftime(datetime.now(), '%Y-%m-%d')
     	# Shaun - Subject and Message to reflect type of notification
	self.subject = self.config.get('subjects', 'prefix') + self.config.get('subjects', reason)
	'''	
	if reason == "motion":
		self.subject = self.config.get('subjects', 'motion')
		msg = self.config.get('messages', 'motion')
	elif reason == "image":
		self.subject = self.config.get('subjects', 'image')
		msg = self.config.get('messages', 'image') + '\n' + msg 
	elif reason == "video":
		self.subject = self.config.get('subjects', 'video')
		msg = self.config.get('messages', 'video') + '\n' + msg
	'''
	m="Date: %s\r\nFrom: %s <%s>\r\nTo: %s\r\nSubject: %s\r\nX-Mailer: My-Mail\r\n\r\n" % (senddate, self.from_name, self.sender, self.recipient, self.subject)
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(self.sender, self.recipient, m + self.config.get('messages', reason) + msg)
        server.quit()    

    def _upload(self, video_file_path, folder_resource, type):
        '''Upload the file and return the doc'''
	if type == 'image':
		mime = 'image/jpeg'
	elif type == 'video':
		mime = 'video/avi'
		
        doc = gdata.docs.data.Resource(type=type, title=os.path.basename(video_file_path))
        media = gdata.data.MediaSource()
        media.SetFileHandle(video_file_path, mime)
        doc = self.client.CreateResource(doc, media=media, collection=folder_resource)
        return doc
    
    def upload_video(self, video_file_path,reason):
        """Upload a video to the specified folder. Then optionally send an email and optionally delete the local file."""
        folder_resource = self._get_folder_resource()
        if not folder_resource:
            raise Exception('Could not find the %s folder' % self.folder)

        doc = self._upload(video_file_path, folder_resource, reason)
                      
        if self.send_email:
            doc_link = None
            for link in doc.link:
		if ('preview' in link.href or 'video.google.com' in link.href):
                    doc_link = link.href
                    break
            # Send an email with the link if found
            msg = '\n\n\nFile Location:'
            if doc_link:
                msg += '\n\n' + doc_link                
            self._send_email(msg,reason)    

        if self.delete_after_upload:
            os.remove(video_file_path)

if __name__ == '__main__':         
    try:
	usage = 'Motion Uploader - sends email notification, uploads videos and images to Google Drive\n   Modified by Shaun Amarelo 2014  --- Originally by Jeremy Blythe (http://jeremyblythe.blogspot.com)\n\n   Usage: uploader.py {motion|video|image} {config-file-path} {video-file-path}'
       	if len(sys.argv) < 3:
		# Shaun Modified
        	exit(usage)
	cmd_reason = sys.argv[1]  #motion | image | video
	
	# Shaun Modified
        cfg_path = sys.argv[2]
        if not os.path.exists(cfg_path):
        	exit('Config file does not exist [%s]' % cfg_path)    
        
	if cmd_reason == "motion":
		msg = ''
		MotionUploader(cfg_path)._send_email(msg,cmd_reason)
	
	else: 
		if len(sys.argv) < 4:
			exit(usage)
		vid_path = sys.argv[3]
		if not os.path.exists(vid_path):
	            exit('Video file does not exist [%s]' % vid_path)    
        	MotionUploader(cfg_path).upload_video(vid_path,cmd_reason)        
    except gdata.client.BadAuthentication:
        exit('Invalid user credentials given.')
    except gdata.client.Error:
        exit('Login Error')
    except Exception as e:
        exit('Error: [%s]' % e)
