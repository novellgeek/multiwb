import sys
import json
import webview

if __name__ == "__main__":
    config_path = sys.argv[1]
    with open(config_path, "r") as f:
        config = json.load(f)

    windows = []
    for win in config["windows"]:
        windows.append(webview.create_window(
            win["title"], win["url"],
            x=win["x"], y=win["y"],
            width=win["width"], height=win["height"],
            fullscreen=win["fullscreen"]
        ))

    webview.start(debug=False)