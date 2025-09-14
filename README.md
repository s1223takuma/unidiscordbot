# Discord Bot

## 概要
この Discord Bot は、テキスト読み上げ・検索・カテゴリ作成・PDF処理・簡単なゲームなど、複数の機能を統合した多機能 Bot です。

主な特徴:
- VC でのテキスト読み上げ (Voicebot)
    - 読み上げ音声の変更
    - サーバーごとの読み上げ辞書登録 
- 検索機能 (Web/News/画像)
- サーバー管理補助機能 (カテゴリ作成・監視)
- PDF 自動展開機能
- ゲーム (人狼)
---

## ファイル構成
```markdown
discord/
├── bot_setup.py
├── main.py
├── .gitignore
├── README.md
├── bot_setup.py
├── automation/
│   ├── observe.py
│   └── pdf_handler.py
├── data/
│   ├── guild_to_kana.json
│   └── voice_setting.json
├── games/
│   └── jinro/
│       ├── manager.py
│       ├── selection.py
│       ├── setup.py
│       ├── status.py
│       └── views.py
├── mycommands/
│   ├── category_manager.py
│   ├── contact.py
│   ├── create_url.py
│   ├── help.py
│   ├── observe_manager.py
│   ├── randomnum.py
│   ├── search.py
│   └── voice.py
└── Voicebot/
    ├── clean_text.py
    ├── ttx.py
    └── voicebot.py
```

