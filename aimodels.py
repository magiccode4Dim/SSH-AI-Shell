import openai
import requests
#classes de conneccao com os modelos de AI
#aimodels.py
class BaseGenie:
    def __init__(self):
        pass

    def ask(self, wish: str, explain: bool = False):
        raise NotImplementedError
    
    def explainOut(self, promptdata):
        raise NotImplementedError
    def post_execute(
        self, wish: str, explain: bool, command: str, description: str, feedback: bool
    ):
        pass
#aimodels.pys
class GeminiModel(BaseGenie):
    def __init__(self, 
    api_key: str, 
    os_fullname: str, 
    shell: str, 
    kernel_release: str):

        self.os_fullname = os_fullname
        self.shell = shell
        self.kernel_release = kernel_release
        self.gemini_api_key = api_key
    def _build_explanation_prompt(self, promptdata):
        explain_text = f"Certifique-se de que a sua descricao tera em conta que o sistema é {self.os_fullname} com o shell {self.shell} e a versão do kernel {self.kernel_release}"
        format_text = "<subtitulo>: <conteudo> Exemplo: Seguranca:existe problema xyz.."

        prompt_list = [
            f"Intrução: Faca uma descricao explicando detalhadamente o que significa este output de terminal: {promptdata}(concidere somente o output originado depois que o usuario inseriu o ultimo comando no sistema).{explain_text}. Nao volte a reescrever o output na descricao. Explique se existe algum problema no output que de certa forma pode causar vulnerabilidades de seguranca ou problemas relacionados a performace do sistema operativo. Se o output indicar a existencia de algum erro aconselhe a como resolver.",
            "Formato da resposta:",
            format_text,
            "Certifique-se de que o formato da sua resposta seja exatamente essa que eu lhe passei.",
        ]
        prompt = "\n\n".join(prompt_list)
        return prompt
    def _build_prompt(self, wish: str, explain: bool):
        explain_text = ""
        format_text = "Command: <escreva_o_comando_aqui>"

        if explain:
            explain_text = (
                "Escreva detalhadamente a descrição por detrás do comando que me enviou."
            )
            format_text += "\nDescri: <escreva_a_descrição_do_comando_aqui>\nA descrição do comando deve ser na mesma lingua que o utilizador está usando."
        format_text += "\nNão inclua paretenses, chavetas ou aspas desnecessárias para o comando funcionar."

        prompt_list = [
            f"Intrução: Escreva um comando para o terminal que faz o seguinte: {wish}. Certifique-se de que este comando vai funcionar no sistema {self.os_fullname} com o shell {self.shell} e esta versão do kernel {self.kernel_release}. {explain_text}",
            "Format:",
            format_text,
            "Certifique-se de que o formato da sua resposta seja exatamente essa que eu lhe passei.",
        ]
        prompt = "\n\n".join(prompt_list)
        return prompt
    def explainOut(self, promptdata):
        prompt = self._build_explanation_prompt(promptdata)
        API_KEY = self.gemini_api_key
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=" + API_KEY

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "contents": [
                {
                    "role": "system",
                    "parts": [
                        {
                            "text": "voçê é um ferramenta que explica output gerado em terminais. Explique ao utilizador, o significado do output que lhe envia"
                        }
                    ],
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data, timeout=15)
        data = response.json()
        text_content = data['candidates'][0]['content']['parts'][0]['text']

        return text_content

    def ask(self, wish: str, explain: bool = False):
        prompt = self._build_prompt(wish, explain)
        #,
        API_KEY = self.gemini_api_key
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key=" + API_KEY

        headers = {
            "Content-Type": "application/json"
        }

        data = {
            "contents": [
                {
                    "role": "system",
                    "parts": [
                        {
                            "text": "voçê é um ferramenta de linha de comando, gere comandos de CLI para o utilizador."
                        }
                    ],
                    "role": "user",
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data, timeout=15)
        data = response.json()
        text_content = data['candidates'][0]['content']['parts'][0]['text']
        ar = text_content.split("\n")
        descri=None
        command=ar[0].split(":")[1]
        if len(ar)==2:
            descri=ar[1].split(":")[1]
        return command,descri

        
#aimodels.pys
class OpenAIModel(BaseGenie):
    def __init__(self, 
    api_key: str, 
    os_fullname: str, 
    shell: str, 
    kernel_release: str):

        self.os_fullname = os_fullname
        self.shell = shell
        self.kernel_release = kernel_release
        openai.api_key = api_key

    def _build_prompt(self, wish: str, explain: bool = False):
        explain_text = ""
        format_text = "Command: <escreva_o_comando_aqui>"

        if explain:
            explain_text = (
                "Escreva detalhadamente a descrição por detrás do comando que me enviou."
            )
            format_text += "\nDescri: <escreva_a_descrição_do_comando_aqui>\nA descrição do comando deve ser na mesma lingua que o utilizador está usando."
        format_text += "\nNão inclua paretenses, chavetas ou aspas desnecessárias para o comando funcionar."

        prompt_list = [
            f"Intrução: Escreva um comando para o terminal que faz o seguinte: {wish}. Certifique-se de que este comando vai funcionar no sistema {self.os_fullname} com o shell {self.shell} e esta versão do kernel {self.kernel_release}. {explain_text}",
            "Format:",
            format_text,
            "Certifique-se de que o formato da sua resposta seja exatamente essa que eu lhe passei.",
        ]
        prompt = "\n\n".join(prompt_list)
        return prompt
    def explainOut(self, promptdata):
        return None

    def ask(self, wish: str, explain: bool = False):
        prompt = self._build_prompt(wish, explain)

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "voçê é um ferramenta de linha de comando, gere comandos de CLI para o utilizador.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=300 if explain else 180,
            temperature=0,
        )
        responses_processed = (
            response["choices"][0]["message"]["content"].strip().split("\n")
        )
        responses_processed = [
            x.strip() for x in responses_processed if len(x.strip()) > 0
        ]
        command = responses_processed[0].replace("Command:", "").strip()

        if command[0] == command[-1] and command[0] in ["'", '"', "`"]:
            command = command[1:-1]

        description = None
        if explain:
            description = responses_processed[1].split("Descri: ")[1]

        return command, description
