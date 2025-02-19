import serial
from pynput.keyboard import Controller, Key

# Define your IR codes and their corresponding actions
ir_code_actions = {
    "DFC03F": "space",  # Example: Spacebar
    "FFA25D": "play_pause",  # Play/Pause
    "FF629D": "volume_up",   # Volume Up
    "FFE21D": "volume_down", # Volume Down
}

# Initialize the keyboard controller
keyboard = Controller()

# Track the last IR code and its state
last_code = None
holding = False  # Flag to indicate if a button is being held

def perform_action(action, hold=False):
    """Perform the action based on the key."""
    if action == "space":
        if hold:
            print("Holding Spacebar")
            keyboard.press(Key.space)  # Press without releasing
        else:
            print("Releasing Spacebar")
            keyboard.release(Key.space)  # Release the key
    elif action == "play_pause":
        print("Toggling Play/Pause")
        keyboard.press(Key.media_play_pause)
        keyboard.release(Key.media_play_pause)
    elif action == "volume_up":
        print("Increasing Volume")
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
    elif action == "volume_down":
        print("Decreasing Volume")
        keyboard.press(Key.media_volume_down)
        keyboard.release(Key.media_volume_down)

def main():
    global last_code, holding

    arduino_port = "COM3"  # Replace with your Arduino's COM port
    baud_rate = 9600

    try:
        with serial.Serial(arduino_port, baud_rate, timeout=0.1) as ser:
            print(f"Connected to Arduino on {arduino_port}. Waiting for IR signals...")
            while True:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    normalized_code = line.strip().upper()[-6:]  # Take the last 6 characters
                    print(f"Received IR code: {normalized_code}")

                    if normalized_code == "FFFFFF":
                        # Repeat code: continue holding the last action
                        if last_code and not holding:
                            action = ir_code_actions.get(last_code)
                            if action:
                                perform_action(action, hold=True)
                                holding = True
                        continue

                    # New button press or release
                    if normalized_code in ir_code_actions:
                        # Release previous key if it's different
                        if holding and last_code != normalized_code:
                            prev_action = ir_code_actions.get(last_code)
                            if prev_action:
                                perform_action(prev_action, hold=False)
                            holding = False

                        # Start holding the new action
                        action = ir_code_actions[normalized_code]
                        perform_action(action, hold=True)
                        last_code = normalized_code
                        holding = True
                    else:
                        # Unknown code or end of press; release key
                        if holding:
                            action = ir_code_actions.get(last_code)
                            if action:
                                perform_action(action, hold=False)
                            holding = False
                            last_code = None
                else:
                    # No signal: release any held key immediately
                    if holding:
                        action = ir_code_actions.get(last_code)
                        if action:
                            perform_action(action, hold=False)
                        holding = False
                        last_code = None

    except serial.SerialException as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        # Ensure all keys are released on exit
        if holding and last_code:
            action = ir_code_actions.get(last_code)
            if action:
                perform_action(action, hold=False)
        print("Exiting...")

if __name__ == "__main__":
    main()
