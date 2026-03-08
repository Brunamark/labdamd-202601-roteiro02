# Tarefa 1

 - O código do cliente não precisou mudar entre as duas execuções, apenas precisou mudar o valor da varíavel `CONFIG_BACKEND`.
-  **`ConfigRepositoryStrategy` (interface):** define o contrato base. Toda implementação deve expor o método `.get(key)`.
**`LocalConfig`:** implementação concreta responsável por ler configurações de JSON local ou HTTP.
  **`get_repo_from_env()`:** factory responsável por escolher e instanciar a estratégia adequada conforme o ambiente.
