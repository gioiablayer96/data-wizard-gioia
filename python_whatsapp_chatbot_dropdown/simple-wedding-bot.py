from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
csrf = CSRFProtect()


# Twilio credentials
ACCOUNT_SID = "AC4a7e56495af72a3c4405f107966c1e77"
AUTH_TOKEN = "495acaf8eb09af61b5640773627bf2ba"
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Twilio sandbox number
MY_WHATSAPP_NUMBER = "whatsapp:+972524550286"  # Your number
client = Client(ACCOUNT_SID, AUTH_TOKEN)

# Send the first message to start the conversation
def send_initial_message():
    print("Attempting to send the initial message...")  # Debugging statement
    message = "Hey, I'm Jean-Pierre, Michael&Gioia wedding bot 🎉 What would you like to know about the partaaay?\n\n" \
              "1️⃣ Wedding location and schedule\n" \
              "2️⃣ E-visa entry requirements for Israel\n" \
              "3️⃣ RSVP\n" \
              "4️⃣ Transportation\n" \
              "5️⃣ Travel recommendations\n" \
              "6️⃣ Wedding registry\n" \
              "7️⃣ Vendor contacts\n" \
              "8️⃣ Recommended airlines\n" \
              "9️⃣ Dinner menu\n" \
              "🔟 Groom and bride contacts\n\n" \
              "Type the number or reply 'menu' to return here."

    client.messages.create(
        from_=TWILIO_WHATSAPP_NUMBER,
        to=MY_WHATSAPP_NUMBER,
        body=message
    )
    print("Initial message sent!")  # Confirm it was executed

# Webhook to handle user responses
@app.route("/webhook", methods=["POST"])
def webhook():
    print("Request received:", request.form)
    incoming_msg = request.form.get("Body").strip().lower()
    print(f"Incoming message: {incoming_msg}")  # Log the received message
    response = MessagingResponse()
    message = response.message()

    # ---- MAIN LOGIC: handle user input ----
    if incoming_msg in ["menu", "back"]:
        send_initial_message()
        message.body("Returning to the main menu... 📋")

    elif incoming_msg in [1, "1", "wedding location", "location"]:
        message.body(
            "\n📍 Wedding Location: Al Hayam, Caesarea, Israel\n"
            "📅 Date: Sunday, June 29, 2025\n"
            "🕘 Schedule:\n"
            "- Reception (Kabalat Panim): 18:30\n"
            "- Ceremony (Chuppa): 19:30 \n"
            "- Dinner and Dancing to follow!!!"
        )

    elif incoming_msg in [2, "2", "e-visa"]:
        message.body(
            "🛂 **E-Visa Entry Requirements**:\n"
            "Here is the link to apply for your E-visa to Israel: "
            "https://israel-entry.piba.gov.il/eligibilitynational/"
        )

    elif incoming_msg in [3, "3", "rsvp"]:
        message.body(
            "🎟 RSVP:\n"
            "Are you attending? Reply with 'Yes' or 'No'.\n"
            "If Yes, how many people? (e.g., 'Yes 2')"
        )
    elif incoming_msg.startswith("yes") or incoming_msg.startswith("no"):
        message.body("✅ Thanks for your response! Your RSVP has been recorded.")

    elif incoming_msg in [4, "4", "transportation"]:
        message.body(
            "🚌 Transportation:\n"
            "Do you need a ride? Join the shuttle group by following this link: https://example.com/busgroup"
        )

    elif incoming_msg in [5, "5", "travel"]:
        message.body(
            "🏨 Travel Recommendations:\n"
            "- Hotels: https://example.com/hotels\n"
            "- Restaurants: https://example.com/restaurants\n"
            "- Attractions: https://example.com/attractions"
        )

    elif incoming_msg in [6, "6", "registry"]:
        message.body(
            "💝 Wedding Registry:\n"
            "Contribute to our honeymoon here: https://example.com/honeymoonfund"
        )

    elif incoming_msg in [7, "7", "vendors"]:
        message.body(
            "📇 Liked our vendors? Contact them!:\n"
            "- Photographer: Jane Doe (jane@example.com)\n"
            "- Caterer: ABC Catering (contact@abc.com)"
        )

    elif incoming_msg in [8, "8", "flying"]:
        message.body(
            "✈️ Recommended Israeli Airlines:\n"
            "- El Al\n"
            "- Arkia\n"
            "- Israir"
        )

    elif incoming_msg in [9, "9", "menu"]:
        message.body(
            "🍽 Dinner Menu:\n"
            "- Starter: Burrata & Tomatoes\n"
            "- Main: Grilled Sea Bass / Vegan Risotto\n"
            "- Dessert: Tiramisu"
        )

    elif incoming_msg in [10, "10", "contact"]:
        message.body(
            "📱Groom & Bride Numbers:\n"
            "- Michael: +972 50-387-6660\n"
            "- Gioia: +972 52-455-0286"
        )

    else:
        # Unrecognized input
        message.body(
            "🤖 I didn't understand that. Please reply with a number (1-10) or 'menu' to return to the main menu."
        )
    print(str(response))
    return str(response)

# table number?
# switch to drop down menu with buttons

# Exempt the /webhook route from CSRF
csrf.exempt(webhook)

if __name__ == "__main__":
    # Send the initial message before starting the app
    send_initial_message()
    print("Flask server starting...")
    app.run(debug=True, use_reloader=False, port=5001)