# Free.fr Checker

# ✨ Features
🔐 Checks Free.fr credentials via https://subscribe.free.fr/login/do_login.pl
🧵 Multi-threaded (configurable thread count)
🌐 Optional SOCKS5 proxy support (with automatic rotation on failure)
🔁 Retry logic for both network errors and invalid attempts
📊 Live centered terminal UI with real-time statistics
🎨 Colored output (ASCII banner in light blue, stats with per-field colors)
💾 Saves valid hits to Valid.txt
🪟 Windows console title updates with live stats
🧹 Auto-clears terminal and hides cursor during execution

# 📁 Requirements
Python 3.7+
Required libraries:
```
pip install requests urllib3 colorama
```
# Usage
1. Prepare input files
combo.txt — one credential per line, in email:password format:
```
text
user1@example.com:password1
user2@example.com:password2
```
# proxies.txt (optional) — one proxy per line. Supported formats:
```
host:port
host:port:user:pass
```
If proxies.txt is missing, the tool runs without proxies (a warning is shown).

# ⚠️ Disclaimer
This project is provided for educational and research purposes only.
The author is not responsible for any misuse, damage, or illegal activity caused by this tool.
Using this tool to access accounts you do not own is illegal and strictly prohibited.
Do not use this software against any system without explicit, written permission from the owner.
The user assumes full responsibility for how this tool is used.
This code is provided "as is", without warranty of any kind, express or implied.
By using this software, you agree to comply with all applicable local, national, and international laws.
If you do not agree with these terms, do not use this tool.
