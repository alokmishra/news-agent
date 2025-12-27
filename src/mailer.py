from mailjet_rest import Client
import os

class EmailSender:
    def __init__(self, config=None):
        api_key = os.getenv('MAILJET_API_KEY')
        api_secret = os.getenv('MAILJET_SECRET_KEY')
        self.sender_email = os.getenv('SENDER_EMAIL') # Functioning as 'From' address
        self.client = Client(auth=(api_key, api_secret), version='v3.1')

    def render_template(self, summaries, date, article_count):
        # Create an HTML string with the summaries
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #34495e; }}
                .meta {{ color: #7f8c8d; font-size: 0.9em; margin-bottom: 20px; }}
                .summary {{ margin-bottom: 30px; }}
                .summary h2 {{ border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
                .summary-content {{ margin-left: 20px; }}
            </style>
        </head>
        <body>
            <h1>Your Daily News Digest</h1>
            <div class="meta">{date} | {article_count} Articles Analyzed</div>
        """
        
        for topic, summary in summaries.items():
            html += f"""
            <div class="summary">
                <h2>{topic}</h2>
                <div class="summary-content">
                    {summary}
                </div>
            </div>
            """
        
        html += """
        </body>
        </html>
        """
        return html

    async def send_email(self, subject, html_content):
        data = {
          'Messages': [
            {
              "From": {
                "Email": self.sender_email,
                "Name": "News Agent"
              },
              "To": [
                {
                  "Email": os.getenv("RECIPIENT_EMAIL"),
                  "Name": "Subscriber"
                }
              ],
              "Subject": subject,
              "HTMLPart": html_content,
              "TextPart": "Your daily news digest is here."
            }
          ]
        }
        
        try:
            result = self.client.send.create(data=data)
            print(f"Mailjet response: {result.status_code}")
        except Exception as e:
            print(f"Failed to send email via Mailjet: {e}")