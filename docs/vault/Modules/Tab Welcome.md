# Tab Welcome

> `trafficlab/gui/tabs/tab_welcome.py` (96 lines)

## Class: `WelcomeTab(QWidget)`

Pure display widget. Reads `media/welcome-trafficlab.md` and renders it in a `QTextBrowser`.

### Layout
- Left sidebar: Logo + version text
- Right: Markdown content browser

### Styling
- Custom CSS with VT323/PxPlus IBM VGA9 fonts
- Background: `#1a1a2e`, accent: `#4da3ff`

## Bugs
1. Markdown path resolves relative to `sys.argv[0]` — fragile if CWD differs
2. Missing markdown file → shows "Missing markdown" with no fallback content

## Related
- [[Main Window]]
