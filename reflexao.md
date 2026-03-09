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

## Tarefa 3

- O princípio de separação entre estado e lógica computacional significa que você deve evitar misturar:

  - estado: os dados, valores e informações que o sistema mantém

  - lógica computacional: as regras, cálculos e decisões que operam sobre esses dados
  
    Isso demonstra que ao colocar um store externo independente da instância  ( Redis) e separar a lógica das decisões da instância, faz com que haja transparência de instância, ou seja, o usuário não consegue perceber em qual instância os seus dados estão persistidos, fazendo com que haja maior confiabilidade.

- Variável global em memória mesmo com as duas instâncias na mesma máquina física não funcionam porque dois processos não compartilham memória. Cada processo tem o seu prórpio espaço na memória no sistema operacional, ou seja, um processo A escreve o estado na memória mas o processo B não vai ler dessa mesmo endereço de memória.

## Tarefa 4

- Migração (Tarefa 3) — o processo A encerra, os dados já estão no Redis, o processo B sobe e lê. Há uma janela de tempo entre um e outro. A conexão do usuário é interrompida e reestabelecida.
  Relocação — a conexão nunca cai do ponto de vista do usuário. Enquanto a transferência acontece, mensagens continuam chegando. Isso é mais difícil porque você precisa:

    - Manter o estado MIGRATING para bufferizar mensagens durante a transição
    - Garantir que nenhuma mensagem seja perdida ou duplicada
    - Reconectar e drenar o buffer na ordem certa
- Não garante. Dois cenários problemáticos:
  - Perda de mensagem — se o processo travar enquanto `state == MIGRATING`, o buffer está só em memória. Tudo que estava no _message_buffer some junto com o processo.
  - Entrega duplicada — a mensagem é enviada via `_ws.send()`, mas a confirmação não chega antes da reconexão. O buffer reenvia a mesma mensagem na nova conexão — o servidor recebe duas vezes.
- Flag booleana só representa dois estados: true or false, e nesse caso, precisamos de 3 estados diferentes com 3 comportamentos distintos.
- Live migration de VMs — quando um hypervisor (como VMware ou KVM) precisa mover uma máquina virtual de um servidor físico para outro sem desligar. A VM continua rodando, conexões de rede continuam ativas, o usuário não percebe. 
  
## Tarefa 5

- Read-your-writes consistency é uma garantia de consistência em que, depois que você grava um dado, suas próximas leituras já enxergam essa própria gravação. Sendo assim, o código não implementa porque um exmeplo de um usuário que escreveu algo, vai para o master mas quando o mesmo usuário precisar ler em sequência, não vai conseguir proque a réplica tem um atraso de sincronização com a master e o código atual não tem como saber se a réplica já recebeu a escrita mais recente. 
- Uma mudança que pode ser realizada é após a escrita, forçar as leituras daquele usuário para a master e quando receber um token de sincronização, a leitura será redirecionada para a réplica.

## Tarefa 6

- Respondida acima.
- Isso é fundamentalmente diferente porque um servidor externo aos dois processos consegue gerenciar ambos os processos para saber qual processo está com o lock para travar o segundo processo e um trheading.lock() que funciona dentro de um único processo só vai conseguir pegar o lock baseado naquele processo, nos métodos do próprio processo e um segundo processo não consegue enxergar o lock do primeiro processo e executa de maneira concorrente.
- Justamente o EX que é um time to live do processo que se travar, o tempo vai estourar e o EX vai liberar o processo para não causar deadlock. O risco residual seria o processo A pode terminar a seção crítica após o TTL expirar. O fluxo problemático seria:
```
Processo A adquire o lock (TTL = 5s)

Processo A trava por 6s (GC longo, swap de memória, etc)

TTL expira — Redis deleta o lock automaticamente

Processo B adquire o lock — entra na seção crítica

Processo A "acorda" e termina — executa o finally

finally chama r.delete(key) — deleta o lock do Processo B

Processo C adquire o lock — agora A e C estão na seção crítica simultaneamente
```
O finally do processo A deletou o lock que não era mais dele. O TTL resolveu o deadlock mas criou uma janela de race condition de novo.
A solução para isso é o processo A gravar um token único no lock na hora que adquire, e só deletar se o token ainda for o dele, garantindo que não deleta o lock de outro processo. Isso é o que o Redlock (algoritmo oficial do Redis para locks distribuídos) implementa.

## Tarefa 7

- As 8 falácias são:
     1) A rede é confiável
     2) A latência é zero
     3) A largura de banda é infinita
     4) A rede é segura
     5) A topologia não muda
     6) Existe apenas um administrador
     7) O custo de transporte é zero
     8) A rede é homogênea
   
"A rede é confiável" - o código assume que a chamada sempre vai retornar um resultado válido. Não trata falha de conexão, o que gera quebra no cogio de uma exceção não tratada.

- async/await quebra a transparência sintaticamente pois o await é uma marca visual obrigatória no código que indica para o desenvolvedor que pode falhar naquele trecho. Nesse caso é uma boa opção porque o desenvolvedor é forçado a perceber que há uma exceção que precisa ser tratada, evitando que falhas de rede quebrem o código silenciosamente igual ao anti_pattern.


## Bloco de reflexão obrigatória

1) Transparência de relocação porque precisa garantir que o buffer de mensagem seja enviada em ordem e enviem extamente apenas uma vez, exigindo que haja um token de confirmação de sincronização da réplica.No código relocacao_websocket.py, o _message_buffer armazena mensagens durante MIGRATING, mas se o processo travar antes do finally, o buffer é perdido, demonstrando que exactly-once é difícil de garantir mesmo com buffer explícito.
   
2) Nos jogos de fps, como Counter Strike, transparência de latência seria péssimo, uma vez que o jogador precisa saber o que está causando o lag, pois pode ser problema de super aquecimento do computador ou até mesmo falta de memória, logo quando exibe a latência como um problema, o jogador sabe que é erro na rede.
   
3)  Foi explicado na tarefa 7 que async/await quebra a transparência sintaticamente pois o await é uma marca visual obrigatória no código que indica para o desenvolvedor que pode falhar naquele trecho. Nesse caso é uma boa opção porque o desenvolvedor é forçado a perceber que há uma exceção que precisa ser tratada, evitando que falhas de rede quebrem o código silenciosamente igual ao anti_pattern.
4)  Já está explicado na tarefa 6: 
> **Por que `multiprocessing` e nao `threading`?**
> O CPython possui o GIL (*Global Interpreter Lock*), que impede que duas threads executem bytecode Python simultaneamente no mesmo processo. Isso significa que uma race condition com `threading` pode nao se manifestar de forma reproduzivel — tornando a demonstracao pedagogicamente imprecisa. Com `multiprocessing` cada processo tem seu proprio espaco de memoria e proprio GIL: a race condition e real, reproduzivel, e reflete com mais fidelidade o cenario de sistemas distribuidos, onde os processos concorrentes estao em maquinas diferentes.

5) A minha maior dificuldade foi entender o código da tarefa 5. Consegui entender bem o conceito mas fiquei com dificuldade de seguir a lógica principalmente pelo conhecimento mais limitado de python, sendo necessário pedir uma parte para a IA me explicar trechos.
