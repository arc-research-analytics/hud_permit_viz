mkdir -p ~/.streamlit/
echo "[theme]
primaryColor = '#969696'
backgroundColor = '#292929'
secondaryBackgroundColor = '#171717'
textColor = '#d9d9d9'
font = 'monospace'
[server]
headless = true
enableCORS = false
port = $PORT
" > ~/.streamlit/config.toml