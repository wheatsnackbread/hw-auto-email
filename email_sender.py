import pandas as pd
import mistune
from appscript import app, k

# Read the CSV into pandas
df = pd.read_csv("output/spon_output.csv")


def draft_email(company, title, email, body_html):
    outlook = app("Microsoft Outlook")
    msg = outlook.make(
        new=k.outgoing_message,
        with_properties={
            k.subject: title,
            k.content: body_html,
        },
    )

    msg.make(
        new=k.recipient,
        with_properties={k.email_address: {k.address: email}},
    )
    msg.open()
    msg.activate()


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
