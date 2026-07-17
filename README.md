# Binance Light Sandbox (QA MVP)

> [English](#english-version) | [繁體中文](#繁體中文版)

---

## English Version

A lightweight sandbox simulating Binance exchange core components for advanced QA automation and performance testing.

### 🏗️ Core Architecture
Four backend service engines running concurrently with a simple frontend interface:
1. **Compliance Engine** - Regulatory and risk checks.
2. **Order Gateway Engine** - Order entry and routing.
3. **Settlement Engine** - Clearing and matching logic.
4. **Market Data Engine** - Real-time ticker and candlestick feeds.
5. **Frontend Interface** - Dashboard for manual operations and monitoring.

### 🚀 Mac Environment Setup

Run the following commands in your Mac Terminal (Zsh) to set up the workspace:

#### 1. Git Config & Remote Link
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git remote add origin <your-repo-url.git>
```

#### 2. System Dependencies Upgrade
```bash
brew update      # Refresh formula lists
brew upgrade     # Upgrade Python, Git, and underlying crypto dependencies
```

#### 3. Python Virtual Environment & Packages
```bash
python3 -m venv .venv                         # Create local virtual environment
source .venv/bin/activate                     # Activate venv
python3 -m pip install --upgrade pip          # Update pip manager
pip install -r requirements.txt                # Install all Python dependencies
```

#### 4. Mandatory Cursor Extensions
Install via `Cmd + Shift + X`:
* **`Python`** (by Microsoft): Auto-complete and PyTest runner.
* **`Error Lens`**: Prints error logs directly on the code line.
* **`YAML`** (by Red Hat): Syntax highlighting for CI/CD pipelines.

---

## 繁體中文版

此專案為幣安交易所的輕量沙盒環境（Light Sandbox），旨在模擬交易所核心元件以利進行進階的 QA 自動化與效能測試。

### 🏗️ 核心架構
後台常駐運行四大核心服務引擎，並搭配輕量前端介面：
1. **Compliance Engine** (合規審查服務)
2. **Order Gateway Engine** (訂單網關接收服務)
3. **Settlement Engine** (交易清算與撮合服務)
4. **Market Data Engine** (即時行情與 K 線數據服務)
5. **Frontend Interface** (提供直觀操作與狀態監控之簡單前端)

### 🚀 Mac 本地作戰環境準備

請依序在 Mac Terminal (Zsh) 執行以下指令以完成環境配置：

#### 1. Git 全域帳戶配置與遠端連結
```bash
git config --global user.name "你的英文名字"
git config --global user.email "你的GitHub信箱"
git remote add origin <你的儲存庫網址.git>
```

#### 2. 系統底層依賴升級
```bash
brew update      # 更新 Homebrew 軟體清單目錄 (拿新菜單)
brew upgrade     # 真正下載並升級本地 Python、Git 等核心工具
```

#### 3. Python 虛擬環境隔離與套件安裝
```bash
python3 -m venv .venv                         # 建立 Mac 本地專屬虛擬環境
source .venv/bin/activate                     # 啟動並切換進入虛擬環境
python3 -m pip install --upgrade pip          # 升級核心套件管理器 pip 到最新版
pip install -r requirements.txt                # 依據清單下載所有 Python 套件
```

#### 4. Cursor 擴充套件推薦
請至 Extensions 商店 (`Cmd + Shift + X`) 安裝：
* **`Python`** (由 Microsoft 出品)：提供智慧型提示與測試框架支援。
* **`Go`** (由 Google 出品)：為未來研究核心後端 Go 服務戴上眼鏡。
* **`Error Lens`**：將語法錯誤即時印在代碼右手邊，殺 Bug 效率最大化。
* **`YAML`** (由 Red Hat 出品)：提供 CI/CD 設定檔的縮排檢查。
