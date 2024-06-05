import pandas as pd
import mistune
from appscript import app, k
from mactypes import Alias
from pathlib import Path

# Read the CSV into pandas
df = pd.read_csv("output/spon_output.csv")


class Outlook(object):
    def __init__(self):
        self.client = app("Microsoft Outlook")


class Message(object):
    def __init__(
        self, parent=None, subject="", body="", to_recip=[], cc_recip=[], show_=True
    ):
        if parent is None:
            parent = Outlook()
        client = parent.client

        self.msg = client.make(
            new=k.outgoing_message,
            with_properties={k.subject: subject, k.content: body},
        )

        self.add_recipients(emails=to_recip, type_="to")
        self.add_recipients(emails=cc_recip, type_="cc")

        if show_:
            self.show()

    def show(self):
        self.msg.open()
        self.msg.activate()

    def add_attachment(self, p):
        # p is a Path() obj, could also pass string
        p = Alias(str(p))  # convert string/path obj to POSIX/mactypes path
        attach = self.msg.make(new=k.attachment, with_properties={k.file: p})

    def add_recipients(self, emails, type_="to"):
        if not isinstance(emails, list):
            emails = [emails]
        for email in emails:
            self.add_recipient(email=email, type_=type_)

    def add_recipient(self, email, type_="to"):
        msg = self.msg

        if type_ == "to":
            recipient = k.to_recipient
        elif type_ == "cc":
            recipient = k.cc_recipient

        msg.make(new=recipient, with_properties={k.email_address: {k.address: email}})


def draft_email(company, title, email, body_html):
    subject = title
    body = body_html
    to_recip = [email]

    msg = Message(subject=subject, body=body, to_recip=to_recip)

    # Attach the file
    p = Path("src/sponpkg.pdf")
    msg.add_attachment(p)

    msg.show()


# Iterate through each row of the dataframe, and call the draft_email function
for index, row in df.iterrows():
    company = row["Company"]
    title = row["Title"]
    email = row["Email"]
    body = row["Response"]

    # Convert markdown to HTML
    markdown = mistune.create_markdown()
    body_html = markdown(body)

    draft_email(company, title, email, body_html)

    print(f"Drafted email for {company} to {email}.")

    # Pause for user to send/close the email
    input("Press Enter after sending/closing the email to proceed to the next one...")

    # If user wants to stop the script, they can type "stop" and the script will break.
    if input("Type 'stop' to stop the script: ") == "stop":
        break

# Save the index of the last email sent
last_index = index
print(f"Last email sent: {last_index} | {company}")
