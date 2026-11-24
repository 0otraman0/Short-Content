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

    def test_grouped_audio_menu_and_standalone_export_and_autopace(self):
        """Test that related audio tools are grouped into an audio menu dropdown table, leaving only Auto-Pace and Export Project on the top bar."""
        html_text = HTML_FILE.read_text(encoding="utf-8")

        # Top bar must have the audio menu toggle
        self.assertIn('id="btn-audio-menu-toggle"', html_text,
                      "Top bar must have a grouped audio menu toggle button (#btn-audio-menu-toggle)")

        # The grouped audio menu container must exist
        self.assertIn('id="audio-menu-dropdown"', html_text,
                      "Audio menu container (#audio-menu-dropdown) must exist")

        # Ensure the audio dropdown contains the related tools
        wrapper_match = re.search(r'<div class="audio-menu-dropdown-wrapper">(.*?)<!-- Giữ độc lập', html_text, re.DOTALL)
        self.assertIsNotNone(wrapper_match, "Could not find .audio-menu-dropdown-wrapper container in HTML")
        menu_html = wrapper_match.group(1)

        self.assertIn('id="preset-selector"', menu_html)
        self.assertIn('id="btn-select-voice"', menu_html)
        self.assertIn('id="btn-audio-fx"', menu_html)
        self.assertIn('id="btn-paragraph-takes"', menu_html)
        self.assertIn('id="btn-preview-audio"', menu_html)
        self.assertIn('id="btn-export-history"', menu_html)

        # Ensure Auto-Pace and Export Audio remain standalone in .top-actions outside the dropdown
        self.assertNotIn('id="btn-auto-pace"', menu_html)
        self.assertNotIn('id="btn-export-project"', menu_html)

    def test_audio_menu_overflow_and_visibility(self):
        """Test that .top-actions and .top-nav do not clip the audio menu dropdown with overflow auto/hidden."""
        css_text = CSS_FILE.read_text(encoding="utf-8")
        js_text = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

        # .top-actions must have overflow: visible
        top_actions_block = re.search(r'\.top-actions\s*\{([^}]*)\}', css_text)
        self.assertIsNotNone(top_actions_block, "Could not find .top-actions block in CSS")
        top_actions_css = top_actions_block.group(1)
        self.assertIn("overflow: visible", top_actions_css,
                      ".top-actions must have 'overflow: visible' so the audio menu dropdown is not clipped vertically.")
        self.assertNotIn("overflow-x: auto", top_actions_css,
                         ".top-actions cannot have 'overflow-x: auto' as it forces vertical clipping of popover dropdowns.")

        # .top-nav must have z-index to stay above the editor
        top_nav_block = re.search(r'\.top-nav\s*\{([^}]*)\}', css_text)
        self.assertIsNotNone(top_nav_block, "Could not find .top-nav block in CSS")
        top_nav_css = top_nav_block.group(1)
        self.assertIn("z-index", top_nav_css,
                      ".top-nav must have a z-index to ensure popover dropdowns float above the editor.")

        # In app.js, outside-click logic must use .contains()
        self.assertIn("!audioMenuToggle.contains(e.target)", js_text,
                      "app.js must use !audioMenuToggle.contains(e.target) to properly handle clicks on toggle children")

    def test_audition_bar_loading_disable_and_cancel(self):
        """Test that audition bar features loading indicator, disables buttons during generation, and supports cancellation."""
        html_text = HTML_FILE.read_text(encoding="utf-8")
        css_text = CSS_FILE.read_text(encoding="utf-8")
        js_text = (STATIC_DIR / "app.js").read_text(encoding="utf-8")

        # HTML must have cancel button in audio preview bar
        self.assertIn('id="btn-cancel-preview"', html_text,
                      "Audition bar must have a cancel button (#btn-cancel-preview)")

        # CSS must define disabled state for .btn-subtle:disabled and cancel button styles
        self.assertIn(".btn-subtle:disabled", css_text,
                      "CSS must define disabled state (.btn-subtle:disabled) to prevent repeat clicks")
        self.assertIn(".btn-cancel-preview", css_text,
                      "CSS must define styles for .btn-cancel-preview")

        # JS must disable buttons, indicate loading status, and support AbortController cancellation
        self.assertIn("btnPreviewParagraph.disabled = true", js_text,
                      "app.js must disable btnPreviewParagraph during audio generation")
        self.assertIn("btnPreviewAll.disabled = true", js_text,
                      "app.js must disable btnPreviewAll during audio generation")
        self.assertIn("AbortController", js_text,
                      "app.js must use AbortController to support cancelling the in-flight TTS generation")
        self.assertIn("cancelAudioPreview", js_text,
                      "app.js must implement cancelAudioPreview to cancel in-flight audio synthesis")

if __name__ == "__main__":
    unittest.main()
