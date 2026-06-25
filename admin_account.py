from werkzeug.security import generate_password_hash


password = "admin123"


hashed_password = generate_password_hash(password)

print("\n Your password:", password)
print(" Hashed password:\n")
print(hashed_password)