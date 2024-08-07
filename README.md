# SSH - ARTIFICIAL INTELLIGENCE SHELL (AI)
![image](https://github.com/user-attachments/assets/42014ce0-253f-4b19-8284-5bbe24c3d59a)
O **ssh-ai-shell é uma ferramenta que permite o uso de modelos de inteligência artificial generativa em terminais**.
**A ferramenta utiliza a IA para transformar instruções enviadas em linguagem natural para comandos compativeis com a máquina utilizada**. O shell aberto, funciona por cima do protocolo SSH, o que significa que funcionará com qualquer distribuição linux.
Com o modelo conectado, e com o shell ssh aberto, o usuario pode enviar prompts, cujas respostas virão sob a forma de comandos Linux.

## Instalação
Requisitos:
* Python >= 3.10;
* pip >= 24.0.
1. Clone o Projeto.
2. No directorio raiz do projeto, e com internet  ligada, execute:
```bash
./install.sh
```
**NOTA**: Caso não funcione por causa do sistema operativo, pode baixar manualmente as dependências requimentes.txt,
e executar o script ssh_ai_shell.sh presente no directorio raiz.

## Como Utilizar?
Para utilizar, o usuário deve primeiro, criar um arquivo de ficheiro de configuração onde estarão presentes todos os dados sobre as caracteristicas da máquina, e do modelo de LLM a ser utilizado.

1. **Criando ficheiro de configuração Para um servidor Debian 10 (ssh), usando AI Google Gemini**
```bash
ssh_ai_shell newconfig --ssh
```
![image](https://github.com/user-attachments/assets/efa05942-b3fa-4fca-8425-a42244994d92)

3. **Criando ficheiro de configuração Manualmente para um rooteador Microtik (--no-ssh), usando AI Google Gemini**
```bash
ssh_ai_shell newconfig
```
![image](https://github.com/user-attachments/assets/96589111-d64d-47da-86b2-5b16dedc2412)


O utilizador passa a enviar prompts depois que conecta-se a maquina remota usando o comando ***'connect'***. Estando conectado, existem 3 modos de operação: 

* 'prompt'>shellask - Envia um prompt para a IA e recebe a resposta em comando.
EXEMPLO:
![image](https://github.com/user-attachments/assets/7fd6c9da-adc2-4d37-a29d-002820733396)
No rooteador microtik:
![image](https://github.com/user-attachments/assets/baaa9844-a221-423b-be96-8ac4794ef40c)

* 'prompt'>shellexplain - A IA deve explicar o que o comando do prompt deve fazer.
EXEMPLO:
![image](https://github.com/user-attachments/assets/b8aca4a4-395c-41b5-b7a9-d74bb14bd309)

* ''>explainoutput - Explica o output do terminal.
EXEMPLO:
![image](https://github.com/user-attachments/assets/9dc6e559-2303-4f1c-96d6-e68dc1ca379e)

## Desinstalar
```bash
./unnistal.sh
```
## CRÉDITOS
As bases deste projeto são os repositórios [Shell Genie](https://github.com/dylanjcastillo/shell-genie) e [paramiko shell](https://github.com/sirosen/paramiko-shell).

BY narcisopascoal97@gmail.com

