# parts_issue_api_v2.py
from flask import Flask, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_cors import CORS

# ------------------- CONFIG ------------------- #
EMAIL_ADDRESS = "scd.microchip@gmail.com"
EMAIL_PASSWORD = "xyih noir mohl zgxe"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
COMPANY_LOGO = "http://sfas.dmsn.lk:8585/SingerSFAS/assets/images/sfas-logo.png"

# ------------------- Flask App ------------------- #
app = Flask(__name__)
CORS(app, resources={r"/send-email": {"origins": "*"}})  # Allow all origins for /send-email

@app.route("/send-email", methods=["POST", "OPTIONS"])
def send_email():
    # Handle preflight request
    if request.method == "OPTIONS":
        response = app.make_default_options_response()
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        return response

    try:
        data = request.get_json()
        required_fields = ["email", "workOrder", "serial", "contact", "dateTime"]
        if not all(field in data and data[field] for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400

        email = data["email"]
        contact_name = data["contact"]  # Use frontend Contact for personalization
        wo = data["workOrder"]
        serial = data["serial"]
        part = data["part"]  
        tracking = data.get("trackingNumber", "")
        date_time = data["dateTime"]  # Get date/time from frontend

        # Create tracking link if tracking number is provided
        if tracking:
            tracking_link = f"https://track.citypak.lk/track?tracking_number={tracking}"
            tracking_html = f'<a href="{tracking_link}" target="_blank" style="color:#0d6efd; text-decoration:none;">{tracking}</a>'
            tracking_note = '<p style="font-size:12px; color:#555;">Please click the tracking number to check delivery status.</p>'
        else:
            tracking_html = "N/A"
            tracking_note = ""

        # ------------------- Email HTML ------------------- #
        html_body = f"""
        <html>
        <head>
        <style>
            body {{
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f7f8fa;
                color: #333;
                margin:0; padding:0;
            }}
            .container {{
                background: #fff;
                border-radius: 12px;
                padding: 30px;
                max-width: 650px;
                margin: 30px auto;
                box-shadow: 0 4px 15px rgba(0,0,0,0.12);
                border-top: 6px solid #0d6efd;
            }}
            .logo {{ text-align:center; margin-bottom:25px; }}
            .logo img {{ width:180px; }}
            .title {{
                font-size:20px;
                font-weight:bold;
                color:#0d6efd;
                text-align:center;
                margin-bottom:15px;
            }}
            .details {{
                background:#f0f4ff;
                border-radius:10px;
                padding:20px;
                margin:20px 0;
                font-size:14px;
            }}
            .footer {{
                text-align:center;
                font-size:12px;
                color:#888;
                margin-top:25px;
            }}
            .disclaimer {{
                color:red;
                font-weight:bold;
                font-size:13px;
                margin-top:15px;
            }}
        </style>
        </head>
        <body>
        <div class="container">
            <div class="logo">
                <img src="{COMPANY_LOGO}" alt="Logo">
            </div>
            <div class="title">Parts Dispatch Notification</div>
            <p>Dear {contact_name},</p>
            <p>This is to notify that the following parts have been dispatched from <b>Singer Computer Division</b> on <b>{date_time}</b>:</p>

            <div class="details">
                <p><b>Work Order:</b> {wo}</p>
                <p><b>Serial Number:</b> {serial}</p>
                <p><b>Part:</b> {part}</p>
                <p><b>Tracking Number:</b> {tracking_html}</p>
                {tracking_note}
            </div>

            <p>Should you have any inquiries, please feel free to contact our service division.</p>

            <p>Best Regards,<br>
            <b>Singer Computer & Mobile Phone Division</b><br>
            Singer Sri Lanka PLC</p>

            <div class="disclaimer">
                This email is confidential. If you are not the intended recipient, please delete it immediately. <br>
                Contact: scd.microchip@gmail.com
            </div>

            <div class="footer">
                © 2025 Singer Computer Division | Powered by SFAS
            </div>
        </div>
        </body>
        </html>
        """

        # ------------------- Email Setup ------------------- #
        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = email
        msg["Subject"] = f"Parts Dispatch Notification - Work Order {wo}"
        msg.attach(MIMEText(html_body, "html"))

        # ------------------- Send Email ------------------- #
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            return jsonify({"error": f"Email sending failed: {e}"}), 500

        return jsonify({"message": f"Email sent successfully to {email}"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8585)
