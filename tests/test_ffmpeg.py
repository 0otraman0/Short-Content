import os
import shutil
import subprocess
from pathlib import Path

def test_ffmpeg_detection():
    # Reproducer: check if ffmpeg is in PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        # Check if it exists in WinGet directory
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        winget_pkg = Path(local_app_data) / "Microsoft" / "WinGet" / "Packages"
        found = list(winget_pkg.glob("Gyan.FFmpeg*/**/bin/ffmpeg.exe"))
        print(f"Reproduced issue: 'ffmpeg' not in PATH, but found in WinGet at: {found}")
        assert len(found) > 0, "FFmpeg should be installed in WinGet packages"
        
        # Test our fix: add to PATH and verify it can run
        bin_dir = str(found[0].parent)
        os.environ["PATH"] = bin_dir + os.pathsep + os.environ["PATH"]
        resolved = shutil.which("ffmpeg")
        assert resolved is not None, "After fix, ffmpeg must be resolved"
        
        # Run ffmpeg -version
        res = subprocess.run([resolved, "-version"], capture_output=True, text=True)
        assert res.returncode == 0, "ffmpeg -version should return 0"
        print("Test Passed: FFmpeg resolved and executed successfully:", res.stdout.splitlines()[0])
    else:
        res = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
        assert res.returncode == 0
        print("FFmpeg already in PATH:", res.stdout.splitlines()[0])

if __name__ == "__main__":
    test_ffmpeg_detection()
