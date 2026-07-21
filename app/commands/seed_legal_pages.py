"""seed-legal-pages — create or update default legal pages.

Usage:
    uv run python app/manage.py seed-legal-pages

Idempotent: re-running updates title/content if they differ.
"""

from datetime import datetime, timezone
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models.legal_page import LegalPage


PRIVACY_CONTENT = """# Privacy Policy

**Last updated: July 20, 2026**

## 1. Information We Collect

We collect information you provide when using the TypeCrafters platform, including:

- **Account information** — name, email address, and profile details when you register.
- **Content** — blog posts, project descriptions, media files, and any other content you create or upload.
- **Communications** — messages sent through the platform and correspondence with support.

## 2. How We Use Your Information

- Provide, maintain, and improve the platform.
- Send administrative messages, updates, and security alerts.
- Respond to your comments, questions, and support requests.
- Monitor usage patterns to improve user experience.

## 3. Data Sharing

We do not sell your personal information. We may share data with trusted third-party services that help us operate the platform (hosting, analytics, email delivery), subject to confidentiality agreements.

## 4. Data Retention

We retain your information for as long as your account is active. You may request deletion of your account and associated data at any time by contacting support.

## 5. Your Rights

Depending on your jurisdiction, you may have the right to:

- Access the personal data we hold about you.
- Request correction or deletion of your data.
- Object to or restrict processing of your data.
- Data portability.

## 6. Contact

For questions about this policy, contact us at [privacy@typecrafters.com](mailto:privacy@typecrafters.com).
"""

TERMS_CONTENT = """# Terms of Service

**Last updated: July 20, 2026**

## 1. Acceptance of Terms

By accessing or using the TypeCrafters platform ("the Service"), you agree to be bound by these Terms of Service. If you do not agree, do not use the Service.

## 2. Account Registration

You are responsible for:

- Maintaining the confidentiality of your login credentials.
- All activity that occurs under your account.
- Notifying us immediately of any unauthorized use.

You must be at least 18 years old to use the Service.

## 3. Acceptable Use

You agree not to:

- Use the Service for any unlawful purpose or in violation of any applicable laws.
- Attempt to gain unauthorized access to any part of the Service.
- Upload or distribute malware, viruses, or harmful code.
- Interfere with or disrupt the integrity or performance of the Service.
- Use the Service to harass, abuse, or harm others.

## 4. Intellectual Property

You retain ownership of any content you submit to the Service. By submitting content, you grant TypeCrafters a non-exclusive, worldwide, royalty-free license to host, store, and display your content solely for the purpose of providing the Service.

## 5. Limitation of Liability

The Service is provided "as is" without warranties of any kind. TypeCrafters shall not be liable for any indirect, incidental, or consequential damages arising from your use of the Service.

## 6. Termination

We reserve the right to suspend or terminate your access to the Service at our sole discretion, without notice, for conduct that we believe violates these Terms or is harmful to other users, us, or third parties.

## 7. Changes to Terms

We may modify these Terms at any time. Changes will be posted on this page with an updated "Last updated" date. Continued use of the Service after changes constitutes acceptance of the new Terms.

## 8. Contact

For questions about these Terms, contact us at [legal@typecrafters.com](mailto:legal@typecrafters.com).
"""

DEFAULT_PAGES = [
    {
        "slug": "privacy",
        "title": "Privacy Policy",
        "content_markdown": PRIVACY_CONTENT,
    },
    {
        "slug": "terms",
        "title": "Terms of Service",
        "content_markdown": TERMS_CONTENT,
    },
]


def _upsert_legal_page(session: Session, data: dict) -> None:
    existing = session.execute(
        select(LegalPage).where(LegalPage.slug == data["slug"])
    ).scalar_one_or_none()

    if existing is None:
        page = LegalPage(
            slug=data["slug"],
            title=data["title"],
            content_markdown=data["content_markdown"],
            created_at=datetime.now(timezone.utc),
        )
        session.add(page)
        session.flush()
        print(f"  Created legal page: {data['slug']}")
    else:
        changed = False
        if existing.title != data["title"]:
            existing.title = data["title"]
            changed = True
        if existing.content_markdown != data["content_markdown"]:
            existing.content_markdown = data["content_markdown"]
            changed = True
        if changed:
            existing.updated_at = datetime.now(timezone.utc)
            session.flush()
            print(f"  Updated legal page: {data['slug']}")
        else:
            print(f"  Legal page up to date: {data['slug']}")


def _seed_legal_pages(args: list[str]):
    engine = create_engine(settings.db_url)

    with Session(engine) as session:
        for data in DEFAULT_PAGES:
            _upsert_legal_page(session, data)

        session.commit()
        print(f"\n  Done — {len(DEFAULT_PAGES)} legal pages seeded.")


def register(registry):
    registry.add(
        name="seed-legal-pages",
        help="Seed default legal pages (privacy, terms). Idempotent.",
        fn=_seed_legal_pages,
    )
