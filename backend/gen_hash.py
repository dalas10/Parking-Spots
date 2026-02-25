import bcrypt
pw = b"Test1234"
h = bcrypt.hashpw(pw, bcrypt.gensalt(12))
print(h.decode())
