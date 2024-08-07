# SSH - ARTIFICIAL INTELLIGENCE SHELL (AI)
![image](https://github.com/user-attachments/assets/42014ce0-253f-4b19-8284-5bbe24c3d59a)
O **ssh-ai-shell é uma ferramenta que permite o uso de modelos de inteligência artificial generativa em terminais**.
**A ferramenta utiliza a IA para transformar instruções enviadas em linguagem natural para comandos compativeis com a máquina utilizada**. O shell aberto, funciona por cima do protocolo SSH, o que significa que funcionará com qualquer distribuição linux.
Com o modelo conectado, e com o shell ssh aberto, o usuario pode enviar prompts, cujas respostas virão sob a forma de comandos Linux.

## Instalação


## Como Utilizar?
Para utilizar, o usuário deve primeiro, criar um arquivo de ficheiro de configuração onde estarão presentes todos os dados sobre as caracteristicas da máquina, e do modelo de LLM a ser utilizado. O utilizador passa a enviar prompts depois que conecte-se a maquina remota usando o comando ***'connect'***. Estando conectado, existem 3 modos de operação: 

* 'prompt'>shellask - Envia um prompt para a IA e recebe a resposta em comando.
* 'prompt'>shellexplain - A IA deve explicar o que o comando do prompt deve fazer.
* >explainoutput - Explica o output do terminal
