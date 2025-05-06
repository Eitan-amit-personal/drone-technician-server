from pymavlink import mavutil
import time

PORT = "COM8"  # או /dev/ttyUSB0 ב־Linux
BAUD = 115200
LUA_PATH = "APM/scripts/AP.lua"

def connect_mavlink(port, baud):
    print(f"🔌 Connecting to {port}...")
    mav = mavutil.mavlink_connection(port, baud=baud)
    mav.wait_heartbeat(timeout=10)
    print("✅ Connected to system", mav.target_system)
    return mav

def read_parameters(mav):
    print("📥 Requesting parameters...")
    mav.mav.param_request_list_send(mav.target_system, mav.target_component)
    while True:
        msg = mav.recv_match(type='PARAM_VALUE', timeout=5)
        if not msg:
            break
        print(f"{msg.param_id} = {msg.param_value}")
    print("✅ Finished reading parameters.\n")


def open_file_read(mav, path):
    payload = bytearray([0x01, 0x01])  # OpenFileRO command
    payload += path.encode("utf-8").ljust(251, b"\x00")
    print("-- sending FTP request --")

    # Sending the FTP OpenFileRO request
    mav.mav.file_transfer_protocol_send(
        0, 0, mav.target_system, mav.target_component, payload
    )
    print("-- FTP request sent --")

    # Receiving the ACK
    ack = mav.recv_match(type='FILE_TRANSFER_PROTOCOL', blocking=True, timeout=3)

    if ack:
        # Debugging: Print full ACK content and type
        print(f"📦 Full ACK data: {ack}")
        print(f"📦 Response payload type: {type(ack.payload)}")
        print(f"📦 Response payload value: {ack.payload}")
        print(f"📦 ACK payload (raw): {list(ack.payload)}")  # Print the raw list of bytes

        # Let's check if the payload is a bytearray
        if isinstance(ack.payload, bytearray):
            try:
                # Extract session ID (adjust position if needed)
                session_id = int.from_bytes(ack.payload[3:7], byteorder='little')
                print(f"📦 Session ID: {session_id}")
                return session_id
            except Exception as e:
                print(f"⚠️ Error extracting session ID: {e}")
                raise
        else:
            print(f"⚠️ Unexpected payload type received: {type(ack.payload)}")
            print(f"⚠️ Payload content: {ack.payload}")
            raise ValueError(f"Unexpected payload type: {type(ack.payload)}")
    else:
        print("⚠️ No ACK received.")
        raise RuntimeError("No response to OpenFileRO")


def read_file_data(mav, session_id):
    file_data = bytearray()
    offset = 0

    while True:
        payload = bytearray([0x02])  # ReadFile command
        payload += session_id.to_bytes(4, 'little')
        payload += offset.to_bytes(4, 'little')
        payload += (239).to_bytes(2, 'little')  # size
        payload += (0).to_bytes(2, 'little')    # burst
        payload = payload.ljust(251, b"\x00")

        mav.mav.file_transfer_protocol_send(
            0, 0, mav.target_system, mav.target_component, payload
        )

        msg = mav.recv_match(type='FILE_TRANSFER_PROTOCOL', blocking=True, timeout=3)
        if not msg or msg.payload[0] != 0x03:
            break

        data = msg.payload[10:]
        if not data:
            break

        file_data += data
        print(f"📦 Received {len(data)} bytes at offset {offset}")
        if len(data) < 239:
            break

        offset += len(data)

    return file_data

def read_lua_script(mav):
    print(f"📂 Requesting Lua script: {LUA_PATH}")
    try:
        session = open_file_read(mav, LUA_PATH)
        content = read_file_data(mav, session)
        text = content.decode("utf-8", errors="ignore").strip('\x00')
        print("📄 Lua Script Content:\n" + "-"*40)
        print(text)
        print("-"*40)
    except Exception as e:
        print("⚠️ Failed to read Lua script:", e)

if __name__ == "__main__":
    mav = connect_mavlink(PORT, BAUD)
    read_parameters(mav)
    read_lua_script(mav)
