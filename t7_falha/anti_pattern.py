# anti_pattern.py — transparencia excessiva: parece uma chamada local
def get_user(user_id: int) -> dict:
    return db.query(f"SELECT * FROM users WHERE id={user_id}")

# O chamador nao tem como saber que isso pode:
#  - Levar 800ms (latencia de rede)
#  - Lancar TimeoutError (rede caiu)
#  - Retornar None silenciosamente e causar KeyError adiante
user = get_user(42)
print(user["name"])   # KeyError silencioso se user for None!