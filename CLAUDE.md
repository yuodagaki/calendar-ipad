# CASIO DASHBOARD — CLAUDE.md

## プロジェクト概要

iPad 向けのリアルタイム・ダッシュボード。CASIOの液晶時計（G-SHOCKなど）の世界観をモチーフにした単一HTMLファイルで構成される。

- **ファイル構成**: `index.html` 1ファイルにHTML・CSS・JSをすべて内包
- **対象デバイス**: iPad（横向き固定想定）。`viewport` でピンチズームを無効化済み
- **言語**: UI表示は日本語・英字混在（CASIO風の全大文字英数字が基本）

## デザイン原則

### CASIO LCD 美学
- **フォント**: 数値表示は `DSEG7Classic`（本物のセグメントフォント）、ラベルは `Share Tech Mono`
- **ゴーストセグメント**: `lcd-ghost` / `temp-ghost` で `8` を重ねて未点灯セグメントを表現する。この表現は必ず維持する
- **スキャンライン**: `.scanlines` の `repeating-linear-gradient` でCRT風のラスター表現
- **テキストスタイル**: UIラベルはすべて全大文字・`letter-spacing` 広め・`monospace` フォント
- **ボーダー＆インセット**: `.watch-inner` の二重枠で筐体感を演出

### レイアウト
```
┌─────────── HEADER (ロゴ / 秒 / テーマボタン) ───────────┐
│                   TIME BLOCK (大型時刻)                   │
├──────────────┬──────────────┬──────────────────────────────┤
│   WEATHER    │   CALENDAR   │   SCHEDULE (次7日のagenda)   │
└──────────────┴──────────────┴──────────────────────────────┘
```
- 単位は `vw` / `vh` で全サイズを相対指定。px固定値は使わない
- flexboxで構成。gridはカレンダー部のみ

## テーマシステム

`T` オブジェクトに3テーマ（`green` / `blue` / `mono`）を定義。

| キー   | 用途                             |
|--------|----------------------------------|
| `body` | ページ背景                       |
| `bg`   | 筐体背景                         |
| `on`   | メイン発光色（アクティブ文字）   |
| `off`  | ゴーストセグメント・境界線暗色   |
| `dim`  | 補助情報・ラベル暗色             |
| `bdr`  | 外枠ボーダー                     |
| `lbl`  | パネルラベル色                   |
| `glow` | テキストシャドウ（発光）         |
| `sun`  | 日曜・祝日の赤                   |
| `sat`  | 土曜の青                         |

新テーマ追加時は `T` に同じキーセットで追加し、`applyTheme()` の `forEach` に名前を追加するだけでよい。

## 外部API

| API | エンドポイント | 更新間隔 | 用途 |
|-----|--------------|---------|------|
| Open-Meteo | `api.open-meteo.com/v1/forecast` | 10分 | 天気・気温・湿度・風速 |
| holidays-jp | `holidays-jp.github.io/api/v1/date.json` | 24時間 | 日本の祝日一覧 |
| カレンダーAPI | `/api/calendar` (ローカル) | 15分 | 予定イベント（失敗時はフォールバック） |

- 座標は `LAT` / `LON` 変数（現在は東京）で変更可能
- `/api/calendar` は失敗しても `renderAgenda()` でフォールバック表示するので、サーバーなしでも動作する

## コーディング規約

- **バニラJS のみ**。フレームワーク・ライブラリは使わない（CDNフォント・DSEGフォントは除く）
- **IE/古いSafari 対応**: `-webkit-` プレフィックスを残す（iPad の古いiOS向け）
- **インラインスタイル vs CSS**: テーマカラーはJSからインラインスタイルで適用。レイアウト・形状はCSSクラスで定義する
- **XSS対策**: ユーザー由来・API由来の文字列は必ず `esc()` 関数を通す
- **`var` 使用**: 既存コードは `var` で統一されているため、追記時も `var` を使う（`let`/`const` に変換しない）

## よくある改修パターン

### 新しいテーマ色を追加
1. `T` オブジェクトに新エントリを追記
2. ボタンHTMLを `<div class="modes">` に追加
3. `applyTheme()` の `['green','blue','mono']` 配列に名前を追加

### カレンダーに機能追加
- `renderCalendar()` がHTMLを文字列で組み立てて `innerHTML` に流し込む方式
- 変更後は必ず `applyTheme()` → `renderCalendar()` の呼び出し順を確認（テーマ適用はカレンダー再描画を伴う）

### 天気情報の項目追加
- `fetchWeather()` のAPIリクエストURLに `hourly=` パラメータを追記
- レスポンスの `d.hourly` から取得して `el.innerHTML` の文字列に組み込む

### アジェンダのイベント表示
- `/api/calendar` が返すJSON形式:
  ```json
  {
    "today": "YYYY-MM-DD",
    "events": [
      { "date": "YYYY-MM-DD", "dayLabel": "月曜", "dateNum": "4/7",
        "allDay": false, "start": "10:00", "end": "11:00",
        "title": "MTG", "calendar": "work" }
    ]
  }
  ```

## 注意事項

- フォントサイズは `vw` 単位のため、ウィンドウ幅が変わると全体比率が保たれる。`px` でサイズを上書きしない
- ゴーストセグメント (`lcd-ghost`, `temp-ghost`) は `position:absolute` で `lcd-real` に重ねている。`lcd-wrap` の `position:relative` と `display:inline-block` は崩さない
- `localStorage` は `try/catch` で保護されているため、プライベートブラウズでも動作する
