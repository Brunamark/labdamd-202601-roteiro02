# Tarefa 1

 - O código do cliente não precisou mudar entre as duas execuções, apenas precisou mudar o valor da varíavel `CONFIG_BACKEND`.
-  **`ConfigRepositoryStrategy` (interface):** define o contrato base. Toda implementação deve expor o método `.get(key)`.
**`LocalConfig`:** implementação concreta responsável por ler configurações de JSON local ou HTTP.
  **`get_repo_from_env()`:** factory responsável por escolher e instanciar a estratégia adequada conforme o ambiente.


# Tarefa 2

- Poderia modificar o método `resolve()` para não buscar no dicionário `SERVICE_REGISTRY` e consultar um serviço dinâmicamente usando um service registry modificando o código para:
```python
    def resolve(self, service_name: str) -> str:
    # Consulta o Consul/etcd em tempo real a cada chamada
        response = requests.get(
            f"{CONSUL_URL}/v1/health/service/{service_name}?passing=true",
            timeout=1
        )
        instances = response.json()
        if not instances:
            raise ValueError(f"Nenhuma instância saudável para '{service_name}'")
        
        # Escolhe uma instância
        chosen = random.choice(instances)
        addr = chosen["Service"]["Address"]
        port = chosen["Service"]["Port"]
        return f"http://{addr}:{port}"
    
  ```
O health checker que vai marcar as instâncias (passing ou critical) e fica perguntando periodicamente se a instância está viva(probe). Caso esteja OK, a instância retorna 200 OK ou pode não responder enviando nada e health checker marca critical e se estiver saudável, marca como passing. Assim, no ServiceLocator quando faz chamada ao service discovery, só retorna as instâncias que estão funcionando e no chosen, escolhe qual das instâncias saudáveis vai utilizar. No caso do consul é um service registry , armazenando a lista de serviços e seus endereços, health checker fazendo probes periódicos e service discovery que vai descobrir qual instâncias estão saudáveis.

- etcd — banco chave-valor distribuído criado pelo projeto CoreOS, hoje parte do ecossistema Kubernetes. O próprio control plane do Kubernetes usa o etcd internamente para armazenar todo o estado do cluster. Serviços se registram escrevendo chaves com leases (TTL automático); se a instância morrer e não renovar o lease, a entrada some sozinha.
  
    Apache ZooKeeper — sistema de coordenação distribuída originalmente desenvolvido no Yahoo, amplamente adotado no ecossistema Hadoop/Kafka. Usa znodes efêmeros: quando a conexão do serviço cai, o znode é removido automaticamente, notificando os watchers registrados. É mais verboso que etcd, mas ainda presente em stacks legadas e no próprio Kafka para eleição de líder.

