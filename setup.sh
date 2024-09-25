mkdir -p ~/.streamlit/
echo "\
[server]\n\
headless = true\n\
enableCORS = false\n\
port = \$PORT\n\
runOnSave = true\n\
" >> ~/.streamlit/config.toml