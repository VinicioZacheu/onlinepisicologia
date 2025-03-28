from app import create_app, db
from app.models import User, AvailabilityDay, AvailabilitySlot
from datetime import date, time, timedelta

app = create_app()

with app.app_context():
    user = User.query.filter_by(email="vinicio@example.com").first()
    if not user:
        print("❌ User not found.")
    else:
        print("✅ Found:", user.name)

        # Clean old data
        db.session.query(AvailabilitySlot).delete()
        db.session.query(AvailabilityDay).delete()
        db.session.commit()

        base = date.today() + timedelta(days=1)

        # Day 1 – Fully Booked
        d1 = AvailabilityDay(psychologist_id=user.id, date=base)
        db.session.add(d1)
        db.session.commit()
        db.session.add(AvailabilitySlot(day_id=d1.id, time=time(9, 0), is_booked=True))
        db.session.add(AvailabilitySlot(day_id=d1.id, time=time(11, 0), is_booked=True))

        # Day 2 – Pending
        d2 = AvailabilityDay(psychologist_id=user.id, date=base + timedelta(days=1))
        db.session.add(d2)
        db.session.commit()
        db.session.add(AvailabilitySlot(day_id=d2.id, time=time(10, 0), is_pending=True))
        db.session.add(AvailabilitySlot(day_id=d2.id, time=time(13, 0)))

        # Day 3 – Available
        d3 = AvailabilityDay(psychologist_id=user.id, date=base + timedelta(days=2))
        db.session.add(d3)
        db.session.commit()
        db.session.add(AvailabilitySlot(day_id=d3.id, time=time(14, 0)))
        db.session.add(AvailabilitySlot(day_id=d3.id, time=time(16, 0)))

        db.session.commit()
        print("✅ Availability inserted for:", user.email)