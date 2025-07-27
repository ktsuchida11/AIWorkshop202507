"""
最小限のMCPサーバー実装
"""
import asyncio

from mcp.server.fastmcp import FastMCP, Context
from datetime import datetime

# サーバーインスタンス作成
mcp = FastMCP("minimal-mcp-server")

# エコーツール定義
@mcp.tool()
async def echo(message: str, ctx: Context) -> str:
    """入力されたメッセージをそのまま返す簡単なツール"""
    await ctx.debug("Starting echo tool")
    await ctx.info(f"input message : {message}")
    return f"Echo: {message}"

# 日時ツール追加
@mcp.tool()
async def get_current_time(ctx: Context) -> str:
    """現在の日時を取得するツール"""
    try:
        await ctx.debug("Fetching current time tool")
        now = datetime.now()
        await ctx.info(f"現在の日時を取得: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        await ctx.error(f"日時取得中にエラー: {str(e)}")
        return "日時の取得に失敗しました。"
    return f"現在の日時: {now.strftime('%Y-%m-%d %H:%M:%S')}"

# 処理の進捗を報告するツールの例
@mcp.tool()
async def process_items(items: list[str], ctx: Context) -> dict:
    """進捗状況の更新を含むアイテムのリストを処理"""
    total = len(items)
    results = []
    
    for i, item in enumerate(items):
        # Report progress as percentage
        await ctx.report_progress(progress=i, total=total)
        
        # Process the item (simulated with a sleep)
        await asyncio.sleep(0.1)
        results.append(item.upper())
    
    # 100%完了を報告
    await ctx.report_progress(progress=total, total=total)
    
    return {"processed": len(results), "results": results}


# toolからresourceの情報を取得する機能
@mcp.tool()
async def summarize_document(document_uri: str, ctx: Context) -> str:
    """リソースURI別にドキュメントを要約"""
    await ctx.debug(f"Summarizing document at {document_uri}")
    # 文書の内容を読む
    content_list = await ctx.read_resource(document_uri)
    
    if not content_list:
        return "Document is empty"
    
    document_text = content_list[0].content
    
    # 例: 簡単な要約を生成 (長さベース)
    words = document_text.split()
    total_words = len(words)
    
    await ctx.info(f"Document has {total_words} words")
    
    # 簡単な要約を返す
    if total_words > 100:
        summary = " ".join(words[:100]) + "..."
        return f"Summary ({total_words} words total): {summary}"
    else:
        return f"Full document ({total_words} words): {document_text}"

# LLM サンプリング　機能の確認
# このツールは、クライアントの LLM を使用してテキストの感情を分析します。
@mcp.tool()
async def analyze_sentiment(text: str, ctx: Context) -> dict:
    """クライアントの LLM を使用してテキストの感情を分析"""
    # 感情分析を求めるサンプリングプロンプトを作成
    prompt = f"次のテキストの感情を、positive、negative、neutralの3つに分類して分析します。「positive」「negative」「neutral」のいずれか1つの単語を出力してください。分析対象テキスト：{text}"
    
    # サンプリングリクエストをクライアントのLLMに送信
    response = await ctx.sample(prompt)
    
    # LLMの応答を処理
    sentiment = response.text.strip().lower()
    
    # 標準的な感情値にマッピング
    if "positive" in sentiment:
        sentiment = "positive"
    elif "negative" in sentiment:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {"text": text, "sentiment": sentiment}

# リソース定義の
@mcp.resource("info://server")
async def server_info() -> str:
    """サーバーに関する情報を提供するリソース"""
    return "これは最小限の設定で作られたMCPサーバーです。"


# 動的リソースの例
# [protocol]://[host]/[path]
@mcp.resource("greeting://{name}")
async def get_greeting(name: str) -> str:
    """名前に基づいた挨拶を返すリソース"""
    return f"こんにちは、{name}さん！"


# JSON データを返すリソース (dict は自動シリアライズ)
@mcp.resource("data://config")
async def get_config() -> dict:
    """アプリケーション構成を JSONとして提供"""
    return {
        "theme": "dark",
        "version": "1.2.0",
        "features": ["tools", "resources"],
    }

# プロンプト定義の例
@mcp.prompt()
async def simple_prompt(text: str) -> str:
    """単純なプロンプトテンプレート"""
    return f"以下のテキストについて考えてください: {text}"

@mcp.prompt()
async def get_google_news_search_prompt(keyword: str) -> str:
    """Googleニュース検索用のプロンプト"""
    return f"{keyword} -ゲーム -スポーツ" # Googleニュースで除外条件を追加して検索するプロンプトです。

@mcp.prompt()
async def get_weather_prompt(city: str) -> str:
    """天気情報取得用のプロンプト"""
    return f"{city}の天気を教えてください。"

@mcp.prompt()
async def get_job_template_prompt() -> str:
    """ジョブテンプレート取得用のプロンプト"""
    return f"""目的を達成するために以下の手順でタスクを細分化して実施してください。
    1. 目的を明確にする 
    2. 必要なリソースや情報を特定する
    3. タスクを分割する
    4. 各タスクの実行方法を決定する
    5. タスクを実行する
    6. 結果を評価する
    7. 必要に応じて調整する
    8. 最終的な成果物を提出する
    9. フィードバックを受け取る
    10. 次のステップを計画する
    これらの手順を実行することで、目的を達成するための道筋が明確になります。
    実行するタスクは以下の通りです。
    """


# メイン実行部分（直接実行する場合）
if __name__ == "__main__":
    mcp.run()