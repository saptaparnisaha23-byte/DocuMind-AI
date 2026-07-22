from app.auth.security import hash_password
from app.auth.security import verify_password

password = "Sapta@123"

hashed = hash_password(password)

print("Original :", password)
print("Hashed   :", hashed)

print(
    verify_password(
        password,
        hashed
    )
)