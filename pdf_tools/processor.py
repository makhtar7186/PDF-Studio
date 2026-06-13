import io
import zipfile

import fitz  # PyMuPDF
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.colors import Color


class PDFProcessor:
    """All PDF transformation operations."""

    # ── Info ──────────────────────────────────────────────────────────────────

    def page_count(self, data: bytes) -> int:
        return len(PdfReader(io.BytesIO(data)).pages)

    def metadata(self, data: bytes) -> dict:
        reader = PdfReader(io.BytesIO(data))
        meta   = reader.metadata or {}
        sizes  = set()
        for page in reader.pages:
            mb   = page.mediabox
            w_mm = round(float(mb.width)  / 72 * 25.4)
            h_mm = round(float(mb.height) / 72 * 25.4)
            sizes.add(f"{w_mm}×{h_mm} mm")
        return {
            "pages":     len(reader.pages),
            "title":     str(meta.get("/Title",    "")) or "—",
            "author":    str(meta.get("/Author",   "")) or "—",
            "creator":   str(meta.get("/Creator",  "")) or "—",
            "producer":  str(meta.get("/Producer", "")) or "—",
            "encrypted": reader.is_encrypted,
            "sizes":     ", ".join(sizes) if sizes else "—",
        }

    def parse_page_ranges(self, text: str, max_pages: int) -> set:
        pages = set()
        for part in text.split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-", 1)
                try:
                    pages.update(range(int(a.strip()) - 1, int(b.strip())))
                except ValueError:
                    pass
            elif part:
                try:
                    pages.add(int(part) - 1)
                except ValueError:
                    pass
        return {p for p in pages if 0 <= p < max_pages}

    # ── Operations ────────────────────────────────────────────────────────────

    def merge(self, files) -> bytes:
        writer = PdfWriter()
        for f in files:
            for page in PdfReader(io.BytesIO(f.read())).pages:
                writer.add_page(page)
            f.seek(0)
        return self._write(writer)

    def compress(self, data: bytes, level: int) -> bytes:
        reader = PdfReader(io.BytesIO(data))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata({})
        if level >= 2:
            quality = 75 if level == 2 else 45
            for page in writer.pages:
                for img in page.images:
                    try:
                        img.replace(img.image, quality=quality)
                    except Exception:
                        pass
                page.compress_content_streams()
        return self._write(writer)

    def split(self, data: bytes, ranges: list) -> list:
        reader  = PdfReader(io.BytesIO(data))
        results = []
        for start, end in ranges:
            writer = PdfWriter()
            for i in range(start, min(end + 1, len(reader.pages))):
                writer.add_page(reader.pages[i])
            results.append(self._write(writer))
        return results

    def split_to_zip(self, data: bytes, ranges: list, prefix: str) -> bytes:
        parts = self.split(data, ranges)
        buf   = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for i, part in enumerate(parts):
                zf.writestr(f"{prefix}_{i + 1}.pdf", part)
        buf.seek(0)
        return buf.getvalue()

    def delete_pages(self, data: bytes, pages_to_delete: set) -> bytes:
        reader = PdfReader(io.BytesIO(data))
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            if i not in pages_to_delete:
                writer.add_page(page)
        return self._write(writer)

    def extract_pages(self, data: bytes, pages_to_keep: set) -> bytes:
        reader = PdfReader(io.BytesIO(data))
        writer = PdfWriter()
        for i in sorted(pages_to_keep):
            if 0 <= i < len(reader.pages):
                writer.add_page(reader.pages[i])
        return self._write(writer)

    def rotate_pages(self, data: bytes, rotation: int, pages_to_rotate=None) -> bytes:
        reader = PdfReader(io.BytesIO(data))
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            writer.add_page(page)
            if pages_to_rotate is None or i in pages_to_rotate:
                writer.pages[i].rotate(rotation)
        return self._write(writer)

    def reorder_pages(self, data: bytes, new_order: list) -> bytes:
        reader = PdfReader(io.BytesIO(data))
        writer = PdfWriter()
        for i in new_order:
            if 0 <= i < len(reader.pages):
                writer.add_page(reader.pages[i])
        return self._write(writer)

    def number_pages(
        self, data: bytes, position: str = "bottom-center",
        start: int = 1, prefix: str = "", font_size: int = 10
    ) -> bytes:
        reader = PdfReader(io.BytesIO(data))
        writer = PdfWriter()
        for i, page in enumerate(reader.pages):
            mb = page.mediabox
            pw, ph = float(mb.width), float(mb.height)
            packet = io.BytesIO()
            c      = rl_canvas.Canvas(packet, pagesize=(pw, ph))
            c.setFont("Helvetica", font_size)
            c.setFillColorRGB(0.3, 0.3, 0.3)
            txt    = f"{prefix}{i + start}"
            margin = 20
            if   position == "bottom-center": c.drawCentredString(pw / 2, margin, txt)
            elif position == "bottom-right":  c.drawRightString(pw - margin, margin, txt)
            elif position == "bottom-left":   c.drawString(margin, margin, txt)
            elif position == "top-center":    c.drawCentredString(pw / 2, ph - margin - font_size, txt)
            elif position == "top-right":     c.drawRightString(pw - margin, ph - margin - font_size, txt)
            elif position == "top-left":      c.drawString(margin, ph - margin - font_size, txt)
            c.save()
            packet.seek(0)
            page.merge_page(PdfReader(packet).pages[0])
            writer.add_page(page)
        return self._write(writer)

    def insert_pages(self, base_data: bytes, insert_data: bytes, position: int) -> bytes:
        base_pages   = list(PdfReader(io.BytesIO(base_data)).pages)
        insert_pages = list(PdfReader(io.BytesIO(insert_data)).pages)
        writer       = PdfWriter()
        if position < 0:
            for p in insert_pages: writer.add_page(p)
            for p in base_pages:   writer.add_page(p)
        else:
            for p in base_pages[:position + 1]: writer.add_page(p)
            for p in insert_pages:              writer.add_page(p)
            for p in base_pages[position + 1:]: writer.add_page(p)
        return self._write(writer)

    def crop_pages(self, data: bytes, left: float, bottom: float, right: float, top: float) -> bytes:
        reader = PdfReader(io.BytesIO(data))
        writer = PdfWriter()
        for page in reader.pages:
            mb = page.mediabox
            pw, ph = float(mb.width), float(mb.height)
            page.mediabox.lower_left  = (pw * left,        ph * bottom)
            page.mediabox.upper_right = (pw * (1 - right), ph * (1 - top))
            writer.add_page(page)
        return self._write(writer)

    def protect(self, data: bytes, user_pw: str, owner_pw: str = "") -> bytes:
        reader = PdfReader(io.BytesIO(data))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.encrypt(user_pw, owner_pw or user_pw)
        return self._write(writer)

    def add_watermark(
        self, data: bytes, text: str,
        opacity: float = 0.15, angle: float = 45.0, font_size: int = 50
    ) -> bytes:
        reader = PdfReader(io.BytesIO(data))
        writer = PdfWriter()
        for page in reader.pages:
            mb = page.mediabox
            pw, ph = float(mb.width), float(mb.height)
            packet = io.BytesIO()
            c      = rl_canvas.Canvas(packet, pagesize=(pw, ph))
            c.setFont("Helvetica-Bold", font_size)
            c.setFillColor(Color(0.55, 0.55, 0.55, alpha=opacity))
            c.saveState()
            c.translate(pw / 2, ph / 2)
            c.rotate(angle)
            c.drawCentredString(0, 0, text)
            c.restoreState()
            c.save()
            packet.seek(0)
            page.merge_page(PdfReader(packet).pages[0])
            writer.add_page(page)
        return self._write(writer)

    def redact(self, data: bytes, search_terms: list) -> tuple:
        """Returns (redacted_bytes, match_count)."""
        doc   = fitz.open(stream=data, filetype="pdf")
        count = 0
        for page in doc:
            for term in search_terms:
                term = term.strip()
                if not term:
                    continue
                for area in page.search_for(term):
                    page.add_redact_annot(area, fill=(0, 0, 0))
                    count += 1
            page.apply_redactions()
        buf = io.BytesIO()
        doc.save(buf, garbage=3, deflate=True)
        doc.close()
        return buf.getvalue(), count

    # ── Internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _write(writer: PdfWriter) -> bytes:
        buf = io.BytesIO()
        writer.write(buf)
        return buf.getvalue()
