#!/usr/bin/python3
"""Sends an email to the help desk technicians."""


def send_simple_message():
    return requests.post(
    "https://api.mailgun.net/v3/sandbox70e3f4405bfb461d9938c3d97dae5318.mailgun.org/messages",
    auth=("api", "6720341af862a54f4079b21044419c32-0996409b-27e54710"),
    data={"from": "Excited User <mailgun@sandbox70e3f4405bfb461d9938c3d97dae5318.mailgun.org>",
	"to": ["sibaquma@gmail.com", "SibabalweQuma@sandbox70e3f4405bfb461d9938c3d97dae5318.mailgun.org"],
	"subject": "Hello",
	"text": "Testing some Mailgun awesomeness!"})
