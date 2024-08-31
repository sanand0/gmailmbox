import base64
import mailbox
import os
from email import message_from_bytes
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying scopes, delete the token.json file
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main(q, mbox, update):
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())
    service = build("gmail", "v1", credentials=creds)
    mbox = mailbox.mbox(mbox)
    mbox_ids = {msg["X-Gmail-Message-ID"] for msg in mbox}

    # Initialize token and message list
    page_token = None
    try:
        while True:
            mbox_count = len(mbox_ids)
            search_params = {"q": q, "userId": "me", "maxResults": 100, "pageToken": page_token}
            results = service.users().messages().list(**search_params).execute()
            messages = results.get("messages", [])
            if not messages:
                break

            # Iterate through each message
            for message in messages:
                if message["id"] in mbox_ids:
                    print(f"SKIP  {message['id']}")
                    continue
                req = service.users().messages().get(userId="me", id=message["id"], format="raw")
                msg = req.execute()
                # Decode the raw message
                raw_email = base64.urlsafe_b64decode(msg["raw"].encode("ASCII"))
                email_message = message_from_bytes(raw_email)
                mbox_message = mailbox.mboxMessage(email_message)
                mbox_message.set_from("MAILER-DAEMON", True)
                mbox_message.add_header('X-Gmail-Message-ID', message["id"])
                mbox.add(mbox_message)
                mbox_ids.add(message["id"])
                print(f"{len(mbox_ids):05d} {message['id']}")

            # If no new emails were added, assume all old emails were added
            if update and mbox_count == len(mbox_ids):
                print("DONE  --update")
                break

            # Get the next page token, if available
            page_token = results.get("nextPageToken")
            if not page_token:
                break
    finally:
        print("CLOSE mbox")
        mbox.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync Gmail to .mbox via the API")
    parser.add_argument("--mbox", type=str, default="emails.mbox", help="Path to .mbox file")
    parser.add_argument(
        "--q", type=str, default="in:anywhere -in:spam -in:trash -invite", help="Gmail search"
    )
    parser.add_argument("--update", action="store_true", help="Only update new emails")

    args = parser.parse_args()
    main(mbox=args.mbox, q=args.q, update=args.update)
