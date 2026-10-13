import subprocess
import tempfile
import unittest
from pathlib import Path

from app.media import MediaError, extract_mp3, ffmpeg_available, safe_stem


class SafeStemTests(unittest.TestCase):
    def test_strips_unsafe_characters(self):
        self.assertEqual(safe_stem("../../etc/pass wd?.mp4"), "pass wd")
        self.assertEqual(safe_stem("***.mp4"), "media")
        self.assertLessEqual(len(safe_stem("a" * 300 + ".mp4")), 80)


@unittest.skipUnless(ffmpeg_available(), "FFmpeg not installed")
class ExtractMp3Tests(unittest.TestCase):
    def test_extracts_audio_from_video(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "clip.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error",
                 "-f", "lavfi", "-i", "testsrc=duration=1:size=160x120:rate=10",
                 "-f", "lavfi", "-i", "sine=frequency=440:duration=1",
                 "-shortest", "-pix_fmt", "yuv420p", str(video)],
                check=True,
            )
            mp3 = extract_mp3(video)
            self.assertEqual(mp3.suffix, ".mp3")
            self.assertGreater(mp3.stat().st_size, 1000)

    def test_video_without_audio_gives_clear_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "silent.mp4"
            subprocess.run(
                ["ffmpeg", "-y", "-loglevel", "error",
                 "-f", "lavfi", "-i", "testsrc=duration=1:size=160x120:rate=10",
                 "-pix_fmt", "yuv420p", str(video)],
                check=True,
            )
            with self.assertRaises(MediaError):
                extract_mp3(video)


if __name__ == "__main__":
    unittest.main()
