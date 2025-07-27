import streamlit as st
from datetime import datetime

from langfuse.openai import openai
from langfuse import get_client
from dotenv import load_dotenv

from fastmcp import Client
from fastmcp.client.logging import LogHandler, LogMessage
import asyncio

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from langfuse import Langfuse

Langfuse(
  secret_key="sk-lf-6b4e2122-c845-4827-b3aa-1dca2ccbafd7",
  public_key="pk-lf-5733f7c8-9561-4379-8499-6a1b9c64e66f",
  host="http://127.0.0.1:3000"
)

langfuse = get_client()
langfuse.flush()

load_dotenv()

# ログハンドラーの定義 コールバックの登録が必要
# ここでは、ログメッセージをコンソールに出力するだけ
async def my_log_handler(params: LogMessage):
    print(f"[Server Log - {params.level.upper()}] {params.logger or 'default'}: {params.data}")


# オプション1：`python my_server.py`経由で実行されるサーバーに接続する（stdioを使用）
client = Client("./src/mcp_servers/test_server.py", log_handler=my_log_handler,)

# オプション2：`fastmcp run ... --transport sse --port 8080`経由で実行されるサーバーに接続する
# client = Client("http://localhost:8080") # 正しいURL/ポートを使用

print(f"クライアントは接続するように構成されました: {client}")

llm_client = openai.OpenAI()

background_prompt = ""

async def interact_with_server(client: Client = None):
    print("--- クライアントを作成 ---")

    try:
        async with client:
            print("--- クライアント接続完了 ---")
            # toolsの一覧を取得します
            tools = await client.list_tools()
            print(f"利用可能なツール: {tools}")
            st.markdown(f"利用可能なツール: {tools}")

            # resourcesの一覧を取得します
            resources = await client.list_resources()
            print(f"利用可能なリソース: {resources}")
            st.markdown(f"利用可能なリソース: {resources}")

            # promptsの一覧を取得します
            prompts = await client.list_prompts()
            print(f"利用可能なプロンプト: {prompts}")
            st.markdown(f"利用可能なプロンプト: {prompts}")

            # 'process_items'ツールを呼び出します
            process_result = await client.call_tool("process_items", {"items": ["リモートクライアント", "リモートサーバー", "MCPツール"]})
            print(f"process結果: {process_result}")
            st.markdown(f"process結果: {process_result.structured_content}")

            # 'echo'ツールを呼び出します
            echo_result = await client.call_tool("echo", {"message": "Hello, MCP!"})
            print(f"echo結果: {echo_result}")
            st.markdown(f"echo結果: {echo_result.structured_content}")

            # 'get_current_time'ツールを呼び出します
            current_time_result = await client.call_tool("get_current_time")
            print(f"現在の日時: {current_time_result}")
            st.markdown(f"現在の日時: {current_time_result.structured_content}")

            # 'summarize_document'ツールを呼び出します
            document_summary = await client.call_tool("summarize_document", {"document_uri": "data://config"})
            print(f"ドキュメント要約: {document_summary}")
            st.markdown(f"ドキュメント要約: {document_summary.structured_content}")

            # 'config'リソースを読み取ります
            config_data = await client.read_resource("data://config")
            print(f"read_resource configリソース: {config_data}")
            st.markdown(f"read_resource configリソース: {config_data}")

            # 'greeting'リソースを読み取ります
            greet_result = await client.read_resource("greeting://リモートクライアント")
            print(f"read_resource greeting: {greet_result}")
            st.markdown(f"read_resource get_prompt greeting: {greet_result}")

            # ユーザーに対して、Googleニュース検索を行うためのプロンプトを作成します
            search_prompt = await client.get_prompt("get_google_news_search_prompt", {"keyword": "AI技術の最新動向"})
            print(f"検索プロンプト: {search_prompt}")
            st.markdown(f"get_prompt 検索プロンプト| input: {{\"keyword\": \"AI技術の最新動向\"}}, output: {search_prompt.messages[0].content}")

            weather_prompt = await client.get_prompt("get_weather_prompt", {"city": "北海道"})
            print(f"検索プロンプト: {weather_prompt}")
            st.markdown(f"get_prompt 検索プロンプト| input: {{\"city\": \"北海道\"}}, output: {weather_prompt.messages[0].content}")

            job_prompt = await client.get_prompt("get_job_template_prompt")
            print(f"検索プロンプト: {job_prompt}")
            st.markdown(f"get_prompt 検索プロンプト| output: {job_prompt.messages[0].content.text}")

            background_prompt = job_prompt.messages[0].content.text
            print(f"バックグラウンドプロンプト: {background_prompt}")

            # clientに対してpingを送信します
            ping_response = await client.ping()
            print(f"Ping応答: {ping_response}")
            st.markdown(f"Ping応答: {ping_response}")

    except Exception as e:
        print(f"エラーが発生しました: {e}")
        st.error(f"エラーが発生しました: {e}")
    finally:
        print("--- クライアントインタラクション終了 ---")


# 本日の日付の取得
current_date = datetime.now().strftime("%Y年%m月%d日")

final_report_generation_prompt = f"""Based on all the research conducted, create a comprehensive, well-structured answer to the overall research brief:
<Research Brief>
research question that the user asked, which you have been researching.
</Research Brief>

Today's date is {current_date}.

Here are the findings from the research that you conducted:
<Findings>
result of the research conducted by the research assistant, including all relevant information and sources gathered from tool calls and web searches.
</Findings>

Please create a detailed answer to the overall research brief that:
1. Is well-organized with proper headings (# for title, ## for sections, ### for subsections)
2. Includes specific facts and insights from the research
3. References relevant sources using [Title](URL) format
4. Provides a balanced, thorough analysis. Be as comprehensive as possible, and include all information that is relevant to the overall research question. People are using you for deep research and will expect detailed, comprehensive answers.
5. Includes a "Sources" section at the end with all referenced links

You can structure your report in a number of different ways. Here are some examples:

To answer a question that asks you to compare two things, you might structure your report like this:
1/ intro
2/ overview of topic A
3/ overview of topic B
4/ comparison between A and B
5/ conclusion

To answer a question that asks you to return a list of things, you might only need a single section which is the entire list.
1/ list of things or table of things
Or, you could choose to make each item in the list a separate section in the report. When asked for lists, you don't need an introduction or conclusion.
1/ item 1
2/ item 2
3/ item 3

To answer a question that asks you to summarize a topic, give a report, or give an overview, you might structure your report like this:
1/ overview of topic
2/ concept 1
3/ concept 2
4/ concept 3
5/ conclusion

If you think you can answer the question with a single section, you can do that too!
1/ answer

REMEMBER: Section is a VERY fluid and loose concept. You can structure your report however you think is best, including in ways that are not listed above!
Make sure that your sections are cohesive, and make sense for the reader.

For each section of the report, do the following:
- Use simple, clear language
- Use ## for section title (Markdown format) for each section of the report
- Do NOT ever refer to yourself as the writer of the report. This should be a professional report without any self-referential language. 
- Do not say what you are doing in the report. Just write the report without any commentary from yourself.

Format the report in clear markdown with proper structure and include source references where appropriate.

<Citation Rules>
- Assign each unique URL a single citation number in your text
- End with ### Sources that lists each source with corresponding numbers
- IMPORTANT: Number sources sequentially without gaps (1,2,3,4...) in the final list regardless of which sources you choose
- Each source should be a separate line item in a list, so that in markdown it is rendered as a list.
- Example format:
  [1] Source Title: URL
  [2] Source Title: URL
- Citations are extremely important. Make sure to include these, and pay a lot of attention to getting these right. Users will often use these citations to look into more information.
</Citation Rules>
"""

def main():

    # タイトルの設定
    st.title("Deep Research API")

    # メッセージの初期化
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # メッセージの表示
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if "tools" in message:
                with st.expander("tool use proccess"):
                    for tool_output in message["tools"]:
                        st.markdown(tool_output)
            st.markdown(message["content"])

    # チャットボットとの対話
    if prompt := st.chat_input("What is up?"):

        # ユーザーのメッセージを表示
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # チャットボットの応答
        with st.chat_message("assistant"):
            expander = st.expander("tool use proccess")
            message_placeholder = st.empty()
            contents = ""
            tool_outputs = []

        if background_prompt !="":
            input_prompt = background_prompt + "\n" + prompt
        else:
            input_prompt = prompt

        print(input_prompt)
        st.session_state.messages.append({"role": "assistant", "content": input_prompt})

        response = llm_client.responses.create(
            model="o3-deep-research",
            input=input_prompt,
            instructions=final_report_generation_prompt,
            tools=[
                {"type": "web_search_preview"},
            ]
        )

        print(response.output_text)
        message_placeholder.markdown(f"**{response.output_text}**")

    # もしmcpチェックボタンを押下したら
    if st.button("MCPチェック"):
        st.session_state.messages.append({"role": "user", "content": "MCPチェック"})
        with st.chat_message("user"):
            st.markdown("MCPチェック")
            asyncio.run(interact_with_server(client))


if __name__ == "__main__":
    main()