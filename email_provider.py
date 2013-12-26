""" This module will provide smtp support for outgoing email and imap support for incoming mail. """


__author__ = 'Chad Dotson'

import email
import imaplib
import smtplib

from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class SendMailMixin:

    _smtp_server = ""
    _smtp_port = 0
    _username = ""
    _password = ""

    def __init__(self, username, password, smtp_server, smtp_port):
        self._smtp_server = smtp_server
        self._smtp_port = smtp_port
        self._username = username
        self._password = password

    def send_text_message(self, from_address, to_address, subject, text):
        msg = MIMEText(text)

        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = subject
        msg.preamble = 'text'

        self._send_mail(msg)

    def send_image_message(self, from_address, to_address, subject, media):
        msg = MIMEMultipart()

        msg['From'] = from_address
        msg['To'] = to_address
        msg['Subject'] = subject
        msg.preamble = 'image'

        img = MIMEImage(media, 'jpg')

        msg.add_header('Content-Disposition', 'attachment', filename='image.jpg')
        msg.attach(img)

        self._send_mail(msg)


    def _send_mail(self, message):
        smtp_connection = smtplib.SMTP(self._smtp_server, self._smtp_port)
        smtp_connection.ehlo()
        smtp_connection.starttls()
        smtp_connection.ehlo()
        smtp_connection.login(self._username, self._password)
        smtp_connection.sendmail(message['From'], [message['To']], message.as_string())
        smtp_connection.quit()


class IMAPMixin:
    _username = ""
    _password = ""
    _imap_server = ""

    def __init__(self, username, password, imap_server):

        self._username = username
        self._password = password
        self._imap_server = imap_server

    def get_messages(self):
        messages = []

        imap_connection = imaplib.IMAP4_SSL(self._imap_server)
        imap_connection.login(self._username, self._password)

        try:
            imap_connection.select()

            #logging.getLogger('').info(imap_connection.status('INBOX', '(MESSAGES UNSEEN)'))

            unread_messages = imap_connection.search(None, 'UNSEEN')[1][0].split()
            #logging.getLogger('').info(unread_messages)
            if not unread_messages == ['']:
                for num in unread_messages:
                    messages.append( email.message_from_string(imap_connection.fetch( num, '(RFC822)')[1][0][1]))
        finally:
            imap_connection.close()
            imap_connection.logout()

        return messages


class EmailProvider(SendMailMixin, IMAPMixin):

    def __init__(self, username, password, smtp_server, smtp_port, imap_server):
        SendMailMixin.__init__(self, username, password, smtp_server, smtp_port)
        IMAPMixin.__init__(self, username, password, imap_server)

