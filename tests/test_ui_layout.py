import unittest
from pathlib import Path
import re

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
HTML_FILE = STATIC_DIR / "index.html"
CSS_FILE = STATIC_DIR / "style.css"

class TestUILayout(unittest.TestCase):
    def test_top_actions_nowrap_and_compact_height(self):
        """Test that top-actions buttons do not wrap text vertically and have compact height."""
        css_text = CSS_FILE.read_text(encoding="utf-8")

        # Must ensure white-space: nowrap on top-actions buttons/selects
        has_nowrap = bool(re.search(r"\.top-actions\s+(?:button|select|\*)[^{]*\{[^}]*white-space\s*:\s*nowrap", css_text))
        self.assertTrue(has_nowrap, "CSS must enforce white-space: nowrap on .top-actions buttons to prevent text wrapping into vertical stacks.")

        # Must ensure height or max-height on top-actions buttons
        has_height = bool(re.search(r"\.top-actions\s+(?:button|select|\*)[^{]*\{[^}]*height\s*:\s*(?:3[0-8]px)", css_text))
        self.assertTrue(has_height, "CSS must enforce a compact height (30-38px) on .top-actions buttons to avoid vertical layout bloating.")

    def test_random_length_button_location(self):
        """Test that btn-random-length is in the editor toolbar with stats/target duration, not overcrowding top-actions."""
        html_text = HTML_FILE.read_text(encoding="utf-8")

        # Find top-actions section
        top_actions_match = re.search(r'<div class="top-actions">(.*?)</div>\s*</header>', html_text, re.DOTALL)
        self.assertIsNotNone(top_actions_match, "Could not find .top-actions container in HTML")
        top_actions_html = top_actions_match.group(1)

        self.assertNotIn('id="btn-random-length"', top_actions_html, 
                         "#btn-random-length should not be in .top-actions; it belongs in .editor-toolbar next to target duration display.")

        # Find editor-toolbar section
        toolbar_match = re.search(r'<div class="editor-toolbar">(.*?)</div>\s*<textarea', html_text, re.DOTALL)
        self.assertIsNotNone(toolbar_match, "Could not find .editor-toolbar container in HTML")
        toolbar_html = toolbar_match.group(1)

        self.assertIn('id="btn-random-length"', toolbar_html,
                      "#btn-random-length must be located in .editor-toolbar next to target duration.")

    def test_assistant_panel_grid_containment(self):
        """Test that app-layout and main-content allow flex/grid shrinking with min-width: 0 so right panel isn't pushed offscreen."""
        css_text = CSS_FILE.read_text(encoding="utf-8")

        # Must have minmax(0, 1fr) in grid-template-columns or min-width: 0 in .main-content
        has_minmax = "minmax(0, 1fr)" in css_text or "minmax(0,1fr)" in css_text
        has_main_content_min_width = bool(re.search(r"\.main-content\s*\{[^}]*min-width\s*:\s*0", css_text))

        self.assertTrue(has_minmax and has_main_content_min_width,
                        "CSS Grid item .main-content and .app-layout must use minmax(0, 1fr) and min-width: 0 to prevent pushing .assistant-panel off-screen on typical laptop displays.")

    def test_pre_export_audition_and_editor_controls(self):
        """Test R2.9 and R5.10 audition controls exist in index.html."""
        html_text = HTML_FILE.read_text(encoding="utf-8")

        # In-editor audition controls (R2.9)
        self.assertIn('id="btn-preview-paragraph"', html_text)
        self.assertIn('id="btn-preview-all"', html_text)
        self.assertIn('id="audio-preview-tag"', html_text)

        # Pre-export review controls (R5.10)
        self.assertIn('id="export-precheck-section"', html_text)
        self.assertIn('id="btn-modal-preview-audio"', html_text)
        self.assertIn('id="export-audition-player"', html_text)
        self.assertIn('id="btn-confirm-start-export"', html_text)

if __name__ == "__main__":
    unittest.main()
