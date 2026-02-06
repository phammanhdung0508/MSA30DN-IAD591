import logging
import queue
import threading

from gemini_client import gemini_generate

logger = logging.getLogger(__name__)

class WhisperWorker:
    def __init__(
        self,
        model: str = "base",
        language: str | None = None,
        task: str = "transcribe",
        on_result=None,
    ) -> None:
        self.model_name = model
        self.language = language
        self.task = task
        self._queue: "queue.Queue[str]" = queue.Queue()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._model = None
        self._on_result = on_result

    def start(self) -> None:
        if self._thread:
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)
        self._thread = None

    def submit(self, wav_path: str) -> None:
        self._queue.put(wav_path)

    def queue_size(self) -> int:
        return self._queue.qsize()

    def _load_model(self) -> None:
        import whisper

        self._model = whisper.load_model(self.model_name)
        logger.info("Whisper model loaded: %s", self.model_name)

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                wav_path = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue
            try:
                if self._model is None:
                    self._load_model()
                result = self._model.transcribe(
                    wav_path,
                    language=self.language or None,
                    task=self.task,
                    temperature=0.0,
                    fp16=False,
                )
                text = (result.get("text") or "").strip()
                logger.info("Whisper text: %s", text)
                if text:
                    gemini = gemini_generate(text)
                    if gemini:
                        logger.info("Gemini result: %s", gemini)
                    if self._on_result:
                        try:
                            self._on_result(wav_path, text, gemini)
                        except Exception:
                            logger.exception("Whisper on_result callback failed")
            except Exception:
                logger.exception("Whisper transcription failed for %s", wav_path)
