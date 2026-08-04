# deskcert-cli (Python)

This is the Python distribution of [DeskCert](https://github.com/RudrenduPaul/DeskCert-CLI) --
a genuine, independent Playwright-Python implementation of the task-runner and scorer, not a
subprocess wrapper around the Node package. See the
[main repository README](https://github.com/RudrenduPaul/DeskCert-CLI#readme) for full docs,
the task-definition format, the CLI reference, and the FAQ.

```
pip install deskcert-cli
playwright install chromium
deskcert init
deskcert serve-fixture &
deskcert run --agent scripted --suite ./deskcert-suite
```
