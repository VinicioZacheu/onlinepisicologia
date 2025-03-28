from app import create_app, db
from app.models import User, AvailabilityDay, AvailabilitySlot

app = create_app()

with app.app_context():
    user = User.query.filter_by(email="vinicio@example.com").first()

    if not user:
        print("❌ Psychologist not found.")
    else:
        print(f"\n🧠 Psychologist: {user.name} (ID: {user.id})")

        days = AvailabilityDay.query.filter_by(psychologist_id=user.id).all()
        if not days:
            print("⚠️ No availability days found.")
        else:
            for day in days:
                print(f"\n📅 {day.date}")
                slots = day.slots
                if not slots:
                    print(" - ❌ No slots")
                for slot in slots:
                    status = (
                        "🟥 Booked" if slot.is_booked else
                        "🟨 Pending" if slot.is_pending else
                        "🟩 Available"
                    )
                    print(f" - ⏰ {slot.time} | {status}")
