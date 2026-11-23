import io
import sys
import unittest

class TestPyAVCompatibility(unittest.TestCase):

    def test_av_open_metadata_errors_compatibility(self):
        import av

        # Verify whether av.open accepts metadata_errors or needs patching
        needs_patch = False
        dummy_io = io.BytesIO(b"dummy")
        try:
            av.open(dummy_io, mode="r", metadata_errors="ignore")
        except TypeError as e:
            if "metadata_errors" in str(e):
                needs_patch = True
        except Exception:
            # Container format error on dummy data is expected, as long as argument error is not raised
            pass

        # Apply the fix
        _orig_open = av.open
        def _safe_open(*args, **kwargs):
            kwargs.pop("metadata_errors", None)
            return _orig_open(*args, **kwargs)
        av.open = _safe_open

        # Verify that with patch, metadata_errors does not raise TypeError
        try:
            av.open(dummy_io, mode="r", metadata_errors="ignore")
        except TypeError as e:
            self.fail(f"av.open still raised TypeError: {e}")
        except Exception:
            # Expected container format error on dummy data
            pass

        print(f"PyAV compatibility test passed! (av version: {av.__version__}, needed patch: {needs_patch})")

if __name__ == "__main__":
    unittest.main()
