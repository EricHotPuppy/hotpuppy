#!/usr/bin/env python3
"""
Database reset script for HotPuppy
Removes all evolution history and starts fresh with a new seed image
"""
import os
import sys
from pathlib import Path

# Delete the database file
db_path = Path("hotpuppy.db")
if db_path.exists():
    db_path.unlink()
    print("✅ Database deleted successfully")
else:
    print("⚠️ Database file not found (already clean)")

print("🔄 Database will be recreated on next application startup")
print("🌱 A new seed image will be generated automatically")
print("")
print("👉 Restart your application now to see the new HotPuppy!")
