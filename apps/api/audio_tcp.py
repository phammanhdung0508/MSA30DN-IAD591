import logging
import os
import socket
import struct
import threading
import time
import wave
from datetime import datetime

logger = logging.getLogger(__name__)


class TcpAudioRecorder:
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 3334,
        save_dir: str = "recordings",
        sample_rate: int = 16000,
        silence_timeout_s: float = 6.0,
        whisper_worker=None,
    ) -> None:
        self.host = host
        self.port = port
        self.save_dir = save_dir
        self.sample_rate = sample_rate
        self.silence_timeout_s = silence_timeout_s
        self._sock = None
        self._thread = None
        self._stop = threading.Event()
        self._wav = None
        self._recording = False
        self._last_packet_ts = 0.0
        self._expected_seq = None
        self._last_payload_len = 0
        self._drop_count = 0
        self._last_drop_log = 0.0
        self._whisper = whisper_worker
        self._current_path: str | None = None

    def start(self) -> None:
        if self._thread:
            return
        os.makedirs(self.save_dir, exist_ok=True)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(1)
        self._sock.settimeout(0.5)
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("TCP audio recorder listening on %s:%d", self.host, self.port)
        if self._whisper:
            self._whisper.start()

    def stop(self) -> None:
        self._stop.set()
        if self._sock:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
        self._close_wav()
        self._thread = None
        if self._whisper:
            self._whisper.stop()

    def is_running(self) -> bool:
        return self._thread is not None

    def is_recording(self) -> bool:
        return self._recording

    def _open_wav(self) -> None:
        if self._wav:
            return
        filename = datetime.now().strftime("wake_%Y%m%d_%H%M%S.wav")
        path = os.path.join(self.save_dir, filename)
        wav = wave.open(path, "wb")
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(self.sample_rate)
        self._wav = wav
        self._current_path = path
        logger.info("Recording started: %s", path)

    def _close_wav(self) -> None:
        if not self._wav:
            return
        try:
            self._wav.close()
        except Exception:
            pass
        self._wav = None
        self._recording = False
        self._expected_seq = None
        self._last_payload_len = 0
        self._drop_count = 0
        self._last_drop_log = 0.0
        if self._whisper and self._current_path:
            self._whisper.submit(self._current_path)
        self._current_path = None
        logger.info("Recording finished")

    def _handle_audio_payload(self, payload: bytes, seq: int | None) -> None:
        if not self._wav or not payload:
            return
        if seq is not None:
            if self._expected_seq is None:
                self._expected_seq = seq
            if seq != self._expected_seq:
                gap = seq - self._expected_seq
                if gap > 0 and self._last_payload_len > 0:
                    silence = b"\x00" * self._last_payload_len
                    for _ in range(gap):
                        self._wav.writeframes(silence)
                    self._drop_count += gap
                    now_ts = time.time()
                    if now_ts - self._last_drop_log > 1.0:
                        logger.warning("TCP audio gap %d packet(s) in last 1s", self._drop_count)
                        self._drop_count = 0
                        self._last_drop_log = now_ts
                else:
                    logger.warning("TCP audio out-of-order packet: seq=%d expected=%d", seq, self._expected_seq)
                    self._expected_seq = seq
            self._expected_seq = (self._expected_seq + 1) & 0xFFFFFFFF
        self._wav.writeframes(payload)
        self._last_payload_len = len(payload)
        self._last_packet_ts = time.time()

    def _process_buffer(self, buf: bytearray) -> bytearray:
        while True:
            if len(buf) < 4:
                return buf
            tag = bytes(buf[:4])
            if tag == b"STRT":
                self._open_wav()
                self._recording = True
                self._last_packet_ts = time.time()
                del buf[:4]
                continue
            if tag == b"STOP":
                self._close_wav()
                del buf[:4]
                continue
            if tag == b"AUD0":
                if len(buf) < 10:
                    return buf
                seq = struct.unpack_from("<I", buf, 4)[0]
                length = struct.unpack_from("<H", buf, 8)[0]
                if len(buf) < 10 + length:
                    return buf
                payload = bytes(buf[10:10 + length])
                self._handle_audio_payload(payload, seq)
                del buf[:10 + length]
                continue
            del buf[:1]
        return buf

    def _check_timeout(self) -> None:
        if not self._recording:
            return
        if (time.time() - self._last_packet_ts) > self.silence_timeout_s:
            logger.warning("TCP audio timeout, closing file")
            self._close_wav()

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                conn, _addr = self._sock.accept()
            except socket.timeout:
                self._check_timeout()
                continue
            except OSError:
                break

            with conn:
                conn.settimeout(0.5)
                buf = bytearray()
                while not self._stop.is_set():
                    try:
                        data = conn.recv(4096)
                        if not data:
                            break
                        buf.extend(data)
                        buf = self._process_buffer(buf)
                    except socket.timeout:
                        self._check_timeout()
                        continue
                    except OSError:
                        break
            self._close_wav()
