#!/usr/bin/python3
"""
quick_user_host_check.py
Replicates the Amenity test flow for User and Host models.
"""

from datetime import datetime

# ------------------------------------------------------------------ #
# Dynamic imports (mimic your Amenity example)
# ------------------------------------------------------------------ #
User = __import__("business.models.user", fromlist=["User"]).User
Host = __import__("business.models.host", fromlist=["Host"]).Host

# ------------------------------------------------------------------ #
# Create a User
# ------------------------------------------------------------------ #
user = User("alice", "alice@example.com")
print(
    f"User {user.username!r} has email {user.email!r} and ID {user.id}\n"
    f"  • created : {user.creation_date}\n"
    f"  • updated : {user.update_date}\n"
)

# Update username and email to trigger setters & timestamp bump
user.username = "alice2"
user.email = "a2@example.com"
print("After update:")
print(f"  • created : {user.creation_date}")
print(f"  • updated : {user.update_date}\n")

# Dump dict
print("User.to_dict() ➜")
for k, v in user.to_dict().items():
    print(f"  {{'{k}': {v}}}")

print("\n" + "-" * 60 + "\n")

# ------------------------------------------------------------------ #
# Create a Host
# ------------------------------------------------------------------ #
host = Host("bob", "bob@example.com", host_rating=4.2)
print(
    f"Host {host.username!r} (rating {host.host_rating}) has ID {host.id}\n"
    f"  • created : {host.creation_date}\n"
    f"  • updated : {host.update_date}\n"
)

# Update rating to show validation & timestamp change
host.host_rating = 4.8
print("After rating update:")
print(f"  • new rating : {host.host_rating}")
print(f"  • updated    : {host.update_date}\n")

# Dump dict
print("Host.to_dict() ➜")
for k, v in host.to_dict().items():
    print(f"  {{'{k}': {v}}}")

print("\nAll manual checks finished.\n")
