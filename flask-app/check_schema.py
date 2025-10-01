#!/usr/bin/env python3
from app import create_app, db
import sqlalchemy as sa

app = create_app()
app.app_context().push()

print("Checking users table schema:")
result = db.session.execute(sa.text('PRAGMA table_info(users)'))
for row in result:
    print(f"  {row[1]} ({row[2]})")
