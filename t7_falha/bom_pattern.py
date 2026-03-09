# bom_pattern.py — transparencia consciente: o contrato e explicito
import asyncio
from typing import Optional

async def fetch_user_remote(
    user_id: int,
    timeout: float = 2.0
) -> Optional[dict]:
    """
    'async' sinaliza que esta operacao pode suspender o event loop.
    'remote' no nome sinaliza chamada de rede, nao operacao local.
    timeout explicito e retorno Optional[dict] forcam o chamador
    a lidar com a possibilidade de falha.
    """
    try:
        await asyncio.sleep(0.1)  # latencia simulada
        return {"id": user_id, "nome": "Usuario Teste"}
    except asyncio.TimeoutError:
        print(f"Timeout buscando user={user_id}")
        return None
    except Exception as e:
        print(f"Servico indisponivel: {e}")
        return None

async def main():
    user = await fetch_user_remote(42)
    if user:
        print("Usuario:", user["nome"])
    else:
        print("Usuario nao disponivel no momento.")

asyncio.run(main())