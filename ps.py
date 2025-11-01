# Please install OpenAI SDK first: `pip3 install openai`
import os
from openai import OpenAI
import llm_info

client = OpenAI(
    api_key=llm_info.api_key,
    base_url=llm_info.base_url)

prompt = """
根据用户输入的需求编写能实现需求的powershell代码，这个代码需要在windows系统中执行。
代码要求：
1. 代码必须在windows系统中执行。
2. 代码必须是powershell代码。
3. 代码必须是全英文的。
4. 不得出现其他任何额外中文内容
5. 直接输出纯PowerShell代码，不要包含任何代码块标记（如```powershell或```）
6. 不要添加任何解释、注释或说明文字，只输出代码本身
"""

def query(query: str)->str:
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
        stream=False
    )
    return response.choices[0].message.content

def write_code(code: str):
    with open("code.ps1", "w") as f:
        f.write(code)

def run_code():
    os.system("powershell.exe -File -ExecutionPolicy Bypass code.ps1")