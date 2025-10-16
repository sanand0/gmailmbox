# GMail Sync

This script lets me sync GMail to .mbox via the API (not IMAP), allowing me to analyze it offline.

## Usage

Clone this repository:

```bash
git clone https://github.com/sanand0/gmailmbox.git
cd gmailmbox
```

On Google Cloud Console, download `credentials.json` into `gmailmbox/`:

- [Create a new project](https://developers.google.com/workspace/guides/create-project)
- [Enable the Gmail API](https://support.google.com/googleapi/answer/6158841)
- [Create OAuth2 Client ID](https://developers.google.com/workspace/guides/create-credentials) for a Desktop app
- Download the JSON as `credentials.json`

<!--
Here is my link: https://console.cloud.google.com/apis/credentials?authuser=2&project=straive-internal-apps
-->

Then install and run:

```bash
# Fetch all emails (excludes spam, trash, and invites by default)
uv run gmailmbox.py --mbox emails.mbox

# Refresh only new emails
uv run gmailmbox.py --mbox emails.mbox --update

# Refresh only new emails matching a query
uv run gmailmbox.py --mbox emails.mbox --update --q "from:user@example.com"
```

This will sync all emails that match the query to the .mbox file.

Parameters:

- `--mbox`: Path to the .mbox file (default: "emails.mbox")
- `--q`: Gmail search query (default: "in:anywhere -in:spam -in:trash -invite")
- `--update`: Only update new emails (default: False)

<!--

In my laptop, I run:

cd ~/code/gmailmbox
uv run gmailmbox.py --mbox ~/Anand/Mail/straive.mbox --update
-->
