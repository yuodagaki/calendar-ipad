# CASIO DASHBOARD

CASIOの液晶時計をモチーフにしたiPad向けリアルタイムダッシュボード。
時刻・天気・カレンダー・スケジュールを一画面に表示する単一HTMLファイルアプリ。

![Theme: Green](https://img.shields.io/badge/theme-green%20%7C%20blue%20%7C%20mono-brightgreen)
![No dependencies](https://img.shields.io/badge/dependencies-none-lightgrey)

## 機能

- **リアルタイム時計** — DSEG7フォントによるLCDセグメント表示（ゴーストセグメント付き）
- **天気情報** — Open-Meteo APIから現在の気温・体感温度・湿度・風速を取得
- **月間カレンダー** — 日本の祝日をハイライト表示、月ナビゲーション対応
- **週間スケジュール** — 今日から7日分の予定を表示（`/api/calendar` 連携対応）
- **3テーマ切替** — グリーン / ブルー / モノクローム、設定は `localStorage` に保存

## 使い方

サーバーなしで動作します。`index.html` をブラウザで開くだけで使えます。

```bash
# ローカルサーバーを使う場合（/api/calendar を利用したい場合は必要）
npx serve .
# または
python3 -m http.server 8080
```

iPadのSafariで開き、「ホーム画面に追加」するとフルスクリーンのウェブアプリとして動作します。

## カスタマイズ

### 座標の変更

`index.html` の先頭付近にある `LAT` / `LON` を変更すると、天気の取得場所が変わります。

```js
var LAT = 35.6762, LON = 139.6503; // デフォルト: 東京
```

### カレンダーAPI連携

`/api/calendar` が以下のJSONを返すエンドポイントを用意すると、スケジュールパネルに予定が表示されます。エンドポイントが存在しない場合は祝日のみ表示するフォールバック動作になります。

```json
{
  "today": "2026-04-07",
  "events": [
    {
      "date": "2026-04-07",
      "dayLabel": "火曜",
      "dateNum": "4/7",
      "allDay": false,
      "start": "10:00",
      "end": "11:00",
      "title": "MTG",
      "calendar": "work"
    }
  ]
}
```

## iPad で常時表示させる設定

ダッシュボードとして常時表示するには、以下の設定をすべて組み合わせて使います。

### 1. ホーム画面に追加（必須）

Safariで `index.html` を開き、共有ボタン →「ホーム画面に追加」。
フルスクリーンのWebアプリとして起動するようになり、Safariのタブ管理による中断が減ります。

### 2. 自動ロックを無効化（必須）

`設定` → `画面表示と明るさ` → `自動ロック` → **なし**

### 3. 低電力モードを無効化

低電力モードが有効だと自動ロックが強制的に30秒になります。

`設定` → `バッテリー` → `低電力モード` → **オフ**

### 4. Screen Wake Lock API をHTMLに追加（推奨）

iOSは長時間放置するとブラウザを一時停止する場合があります。
`index.html` の `/* ── INIT ──` ブロックの末尾に以下を追記すると、OSレベルのスリープを抑制できます。

```js
// Screen Wake Lock（iOS 16.4以降のSafariで対応）
if ('wakeLock' in navigator) {
  var _wakeLock = null;
  function acquireWakeLock() {
    navigator.wakeLock.request('screen').then(function(lock) {
      _wakeLock = lock;
      lock.addEventListener('release', acquireWakeLock); // 解放されたら再取得
    }).catch(function() {});
  }
  acquireWakeLock();
  document.addEventListener('visibilitychange', function() {
    if (document.visibilityState === 'visible') acquireWakeLock();
  });
}
```

### 5. Guided Access でキオスクモード（オプション）

他のアプリに切り替えられたくない場合に使います。

1. `設定` → `アクセシビリティ` → `Guided Access` → **オン**
2. ダッシュボードを表示した状態でサイドボタンを3回押す
3. `Guided Access を開始` をタップ

解除するにはサイドボタンを3回押してパスコードを入力します。

### 6. 充電しながら運用（必須）

常時表示はバッテリーを継続的に消費します。充電ケーブルを接続した状態で運用してください。

---

## 外部リソース

| リソース | 用途 |
|---------|------|
| [DSEG7 Classic](https://www.keshikan.net/fonts-e.html) (CDN) | LCD セグメントフォント |
| [Share Tech Mono](https://fonts.google.com/specimen/Share+Tech+Mono) (Google Fonts) | ラベル・UIフォント |
| [Open-Meteo API](https://open-meteo.com/) | 天気データ（無料・APIキー不要） |
| [holidays-jp](https://holidays-jp.github.io/) | 日本の祝日データ |

## 動作環境

- iPad Safari（iOS 14以降推奨）
- デスクトップブラウザ（Chrome / Safari / Firefox）
- サーバー不要（`/api/calendar` 連携を除く）
