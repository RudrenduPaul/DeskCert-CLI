Output "/tmp/deskcert-cli-demo/docs/demo-run-json.gif"
Set FontSize 16
Set Width 760
Set Height 260
Set Theme "Dracula"
Set WindowBar Colorful
Set WindowBarSize 36

Type "export PS1='$ '"
Enter
Sleep 300ms
Type "export HOME=/tmp/deskcert-cli-demo"
Enter
Sleep 300ms

Type "deskcert init --dir ./agent-suite"
Enter
Sleep 2s

Type "node ./agent-suite/fixture-app/server.mjs > /dev/null 2>&1 &"
Enter
Sleep 1s

Type "deskcert run --suite ./agent-suite --agent scripted --headless true --json | head -n 25"
Enter
Sleep 6s
