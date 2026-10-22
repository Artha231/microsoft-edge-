import json
import time
from datetime import datetime
import websocket  # pip install websocket-client

WS_URL = "wss://ws.triv.co.id/cable?key=a830d1f85d8c47dfbd21b3935fd10e16"

# ANSI color codes
class C:
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    GRAY   = "\033[90m"
    RESET  = "\033[0m"
    BOLD   = "\033[1m"


def log(msg, color=C.RESET):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{ts}] {msg}{C.RESET}")


def on_open(ws):
    log("Connection Established!", C.GREEN)

    subscribe_msg = {
        "command": "subscribe",
        "identifier": json.dumps({"channel": "Markets::OrderNotifChannel"})
    }
    log("Sending Subscribe Command...", C.GRAY)
    ws.send(json.dumps(subscribe_msg))


def on_message(ws, message):
    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        log(f"Raw non-JSON message: {message}", C.GRAY)
        return

    msg_type = data.get("type")

    if msg_type == "ping":
        # ActionCable ping — tidak perlu log, cuma heartbeat
        return

    if msg_type == "welcome":
        log("Welcome received from server", C.GRAY)
        return

    if msg_type == "confirm_subscription":
        log("Subscription Confirmed! Monitoring data...", C.GREEN)
        return

    if msg_type == "reject_subscription":
        log("Subscription REJECTED by server", C.RED)
        return

    if "message" in data:
        leaked = data["message"]
        log(f"{C.BOLD}DATA LEAKED: {json.dumps(leaked, indent=2)}{C.RESET}", C.YELLOW)
        print(f"{C.GRAY}Full object: {data}{C.RESET}")
    else:
        log(f"Unhandled message: {message}", C.GRAY)


def on_error(ws, error):
    log(f"WebSocket Error: {error}", C.RED)


def on_close(ws, close_status_code, close_msg):
    log(f"Connection Closed (Code: {close_status_code}, Reason: {close_msg})", C.GRAY)


def main():
    log(f"Attempting to connect to: {WS_URL}", C.GRAY)

    ws = websocket.WebSocketApp(
        WS_URL,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    # run_forever akan reconnect otomatis kalau koneksi drop
    ws.run_forever(
        ping_interval=30,      # kirim ping tiap 30 detik
        ping_timeout=10,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("Interrupted by user. Exiting...", C.GRAY)