import os
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_community.chat_models.gigachat import GigaChat

load_dotenv('.env')

# class GigaChatLangChain:
#     def init(self):
#         self.api_key = os.getenv('GIGACHAT_API_KEY')
#         self.client_id = os.getenv('GIGACHAT_CLIENT_ID')
#         self.client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
        
#         print("🔐 Инициализируем LangChain GigaChat...")
        
#         if self.api_key:
#             self.llm = GigaChat(
#                 credentials=self.api_key,
#                 verify_ssl_certs=False,
#                 model="GigaChat",
#                 temperature=0.7
#             )
#         elif self.client_id and self.client_secret:
#             self.llm = GigaChat(
#                 credentials=f"{self.client_id}:{self.client_secret}",
#                 verify_ssl_certs=False,
#                 model="GigaChat",
#                 temperature=0.7
#             )
#         else:
#             raise Exception("❌ Не найдены credentials")
        
#         print("✅ LangChain GigaChat готов!")
    
#     def invoke(self, message):
#         """Используем LangChain invoke"""
#         try:
#             response = self.llm.invoke([HumanMessage(content=message)])
#             return response.content
#         except Exception as e:
#             return f"❌ Ошибка: {e}"

def main():
    print("🚀 GigaChat через LangChain")
    print("=" * 50)
    try:
        chat = GigaChat(credentials=os.getenv('GIGACHAT_API_KEY'), model="GigaChat", temperature=0.7, verify_ssl_certs=False)
        response = chat.invoke([HumanMessage(content="Hello, how are you?")])
        print(response.content)
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()