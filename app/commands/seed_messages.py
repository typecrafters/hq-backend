"""seed-messages — insert mock contact messages for testing.

Usage:
    uv run python app/manage.py seed-messages [--mark-read N] [--clear]
"""

import argparse
from datetime import datetime, timezone

from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.message import Message


MOCK_MESSAGES = [
    {"full_name": "Carlos Mendoza", "email": "carlos@example.com", "message": "Hi, I'd like to inquire about your enterprise plan pricing. We're a team of 15 and interested in the annual subscription."},
    {"full_name": "Sofia Reyes", "email": "sofia@test.org", "message": "I'm having trouble logging into my account. It says 'invalid credentials' even after resetting my password."},
    {"full_name": "Liam Chen", "email": "liam@dev.io", "message": "Your API documentation is excellent! Is there a rate limit for the v2 endpoints? Couldn't find it in the docs."},
    {"full_name": "Emma Wilson", "email": "emma@agency.com", "message": "We'd love to feature your product in our monthly newsletter reaching 50k subscribers."},
    {"full_name": "Diego Morales", "email": "diego@startup.dev", "message": "The latest deployment broke our integration. Error 500 on the webhook callback endpoint. Can you please check urgently?"},
    {"full_name": "Aisha Patel", "email": "aisha@edu.in", "message": "Is there an academic discount program? We're a university lab looking to use your platform for research purposes."},
    {"full_name": "James O'Brien", "email": "james@eire.net", "message": "Feature request: please add CSV export functionality to the dashboard. Manual copying is becoming tedious."},
    {"full_name": "Yuki Tanaka", "email": "yuki@creativa.jp", "message": "Just wanted to say your team's support response time is incredible. Every ticket resolved within 2 hours."},
    {"full_name": "Maria Silva", "email": "maria@consult.br", "message": "I cancelled my subscription last month but I'm still being charged. Please process a refund."},
    {"full_name": "Omar Hassan", "email": "omar@build.ae", "message": "Security concern: session timeout is 30 days by default. Our compliance requires 8 hours max. Can we configure this?"},
    {"full_name": "Priya Sharma", "email": "priya@saas.in", "message": "Thanks for the quick fix on the dashboard bug. Works perfectly now. Very happy with the update."},
    {"full_name": "Tomas Guerrero", "email": "tomas@agencia.es", "message": "Need help migrating from our current provider. Do you offer a migration tool for importing existing data?"},
    {"full_name": "Nina Johansson", "email": "nina@nordic.se", "message": "Your pricing page shows $49/mo but checkout shows $59. There's a discrepancy — please clarify."},
    {"full_name": "Wei Zhang", "email": "wei@tech.cn", "message": "Bug report: search stops working after 3-4 queries. Needs full refresh to resume. Using Chrome 125."},
    {"full_name": "Sarah Mitchell", "email": "sarah@ml.ai", "message": "Do you support SAML/SSO integration? Our enterprise requires Okta for all third-party services."},
]


def _seed_messages(args: list[str]):
    parser = argparse.ArgumentParser(prog="seed-messages")
    parser.add_argument("--mark-read", type=int, default=0, help="Mark first N messages as read")
    parser.add_argument("--clear", action="store_true", help="Delete all messages first")
    parsed = parser.parse_args(args)

    engine = create_engine(settings.database_url())

    with Session(engine) as session:
        if parsed.clear:
            count = session.execute(delete(Message))
            session.commit()
            print(f"Deleted all messages")
            return

        created = []
        for m in MOCK_MESSAGES:
            now = datetime.now(timezone.utc)
            msg = Message(
                subject=m["full_name"],
                mail_to=m["email"],
                content=m["message"],
                sent_at=now,
            )
            session.add(msg)
            session.flush()
            created.append(msg)

        n_read = min(parsed.mark_read, len(created))
        for msg in created[:n_read]:
            msg.read_at = datetime.now(timezone.utc)

        session.commit()

        for msg in created:
            read = "read" if msg.read_at else "unread"
            print(f"  #{msg.id} {msg.subject:<20s} [{read}]")

        print(f"\nDone: {len(created)} created, {n_read} marked as read")


def register(registry):
    registry.add(
        name="seed-messages",
        help="Insert mock contact messages for testing (--mark-read N, --clear)",
        fn=_seed_messages,
    )
