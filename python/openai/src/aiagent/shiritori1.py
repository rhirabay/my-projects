import json
import time

import openai
client = openai.OpenAI()

player_prompt = """
あなたはゲームのプレイヤーです。
ユーザーから指示のあったゲームについて世間一般的なルールに従って
別のプレイヤーに勝てるよう振る舞ってください。
発言は端的に行なってください。
"""

game_master_prompt = """
あなたはゲームマスターです。
ユーザーから指示のあったゲームについて世間一般的なルールに従って
ゲームの進行・勝ち負けの判断を行なってください。

ゲームには「Player1」と「Player2」が参加しています。

判断の結果を以下のjson形式でjsonのみ返却してください。
{
    "winner": "Player1 or Player2 or null。勝負が決定した場合に、勝者の名前を設定",
    "next": "Player1 or Player2 or null。勝負が決まらなかった場合に、次の手番を設定。"
    "message": "ゲームの状況に応じたメッセージ　※プロフェッショナルかつ友好的な表現をすること"
}

・最初の手番はランダムにPlayer1もしくはPlayer2をあなたの独断で選択してください。
・Player1, Payler2の言動ではなく、常に一般的なルールに従って判断してください。
"""

# アシスタントを生成
player1 = client.beta.assistants.create(
    name="プレイヤー１",
    instructions=player_prompt,
    tools=[],
    model="gpt-4o-mini",
)
player2 = client.beta.assistants.create(
    name="プレイヤー２",
    instructions=player_prompt,
    tools=[],
    model="gpt-4o-mini",
)
game_master = client.beta.assistants.create(
    name="ゲームマスター",
    instructions=game_master_prompt,
    tools=[],
    model="gpt-4o-mini",
)


def run_assistant(assistant_id: str) -> str:
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
        response_format="auto",
    )

    while True:
        # スレッドの実行結果を取得
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

        if run.status == 'in_progress' or run.status == 'queued':
            """
            実行中/実行前の場合は、1秒待って再実行
            """
            time.sleep(1)
        elif run.status == 'completed':
            """
            処理完了の場合は、応答を表示
            """
            response = client.beta.threads.messages.list(
                thread_id=thread.id
            )

            return response.data[0].content[0].text.value
        else:
            """
            想定外のステータスの場合は、statusとその他の情報を出力してエラーメッセージを返却
            """
            print(run.status)
            print(run)
            raise Exception(f"assistantの実行中に想定外のステータスを検知しました（ステータス={run.status}）")


# スレッドを生成
thread = client.beta.threads.create()

user_message = input("指示を入力してください: ")
#user_message = "しりとりをしてください。最初の単語は「しりとり」です。"
print(f"User: {user_message}")

# スレッドにメッセージを追加
client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=user_message
)

# ゲームを開始

# 最大 10回ループ（ゲームマスタが進行　→　プライヤーが発言を繰り返す）
for i in range(10):
    print(f"### Turn {i+1}")
    game_master_response = run_assistant(game_master.id)
    game_master_response = json.loads(game_master_response)
    print(f"GameMaster: {game_master_response['message']}")

    if game_master_response['winner'] is not None:
        break

    next_player = game_master_response['next'] == 'Player1' and player1 or player2
    player_response = run_assistant(next_player.id)
    print(f'{game_master_response["next"] }: {player_response}')
