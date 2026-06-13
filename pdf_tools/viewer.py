import base64
import io

import fitz
import streamlit as st
from pypdf import PdfReader


class PDFViewer:
    """Renders PDF previews and thumbnail grids inside Streamlit."""

    @st.cache_data(show_spinner=False)
    def _render_pages(_self, data: bytes, dpi: int) -> list:
        """Return list of base64-encoded PNG strings, one per page."""
        doc    = fitz.open(stream=data, filetype="pdf")
        zoom   = dpi / 72
        matrix = fitz.Matrix(zoom, zoom)
        images = []
        for page in doc:
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            images.append(base64.b64encode(pix.tobytes("png")).decode())
        doc.close()
        return images

    def show_preview(self, pdf_bytes: bytes, key: str, title: str = "Aperçu du document") -> None:
        n_pages = len(PdfReader(io.BytesIO(pdf_bytes)).pages)
        if n_pages == 0:
            st.warning("Document vide.")
            return

        state_key = f"_viewer_page_{key}"
        btn_flag  = f"_nav_btn_{key}"

        if state_key not in st.session_state:
            st.session_state[state_key] = 0

        if st.session_state.get(btn_flag):
            st.session_state[f"psel_{key}"] = st.session_state[state_key] + 1
            st.session_state[btn_flag] = False

        cur = st.session_state[state_key]

        with st.spinner("Génération de l'aperçu…"):
            thumb_imgs = self._render_pages(pdf_bytes, dpi=72)
            main_imgs  = self._render_pages(pdf_bytes, dpi=150)

        thumbs_html = "".join(
            f'<div class="thumb-item {"active" if i == cur else ""}" id="thumb_{key}_{i}">'
            f'<img src="data:image/png;base64,{b64}" alt="Page {i+1}">'
            f'<div class="thumb-num">{i+1}</div></div>'
            for i, b64 in enumerate(thumb_imgs)
        )

        size_label = self._fmt_size(len(pdf_bytes))
        st.markdown(f"""
        <div class="viewer-wrap">
          <div class="viewer-header">
            <div class="viewer-title">👁️ {title}</div>
            <div class="viewer-info">{size_label} · {n_pages} page{"s" if n_pages > 1 else ""}</div>
          </div>
          <div class="viewer-body">
            <div class="thumb-panel">{thumbs_html}</div>
            <div class="main-view">
              <img src="data:image/png;base64,{main_imgs[cur]}" alt="Page {cur+1}">
            </div>
          </div>
          <div class="viewer-footer">
            <span class="page-badge">Page {cur+1} / {n_pages}</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        nav_cols = st.columns([1, 2, 1])
        with nav_cols[0]:
            if st.button("◀ Précédente", key=f"prev_{key}", disabled=(cur == 0)):
                st.session_state[state_key] = cur - 1
                st.session_state[btn_flag]  = True
                st.rerun()
        with nav_cols[1]:
            page_sel = st.selectbox(
                "Aller à la page", options=list(range(1, n_pages + 1)),
                index=cur, key=f"psel_{key}", label_visibility="collapsed",
            )
            if page_sel - 1 != cur:
                st.session_state[state_key] = page_sel - 1
                st.rerun()
        with nav_cols[2]:
            if st.button("Suivante ▶", key=f"next_{key}", disabled=(cur == n_pages - 1)):
                st.session_state[state_key] = cur + 1
                st.session_state[btn_flag]  = True
                st.rerun()

    def show_grid(self, pdf_bytes: bytes, key: str) -> None:
        imgs  = self._render_pages(pdf_bytes, dpi=96)
        items = "".join(
            f'<div class="page-grid-item">'
            f'<img src="data:image/png;base64,{b64}" alt="Page {i+1}">'
            f'<div class="page-grid-num">{i+1}</div></div>'
            for i, b64 in enumerate(imgs)
        )
        st.markdown(f'<div class="page-grid">{items}</div>', unsafe_allow_html=True)

    @staticmethod
    def _fmt_size(n: int) -> str:
        if n < 1024:        return f"{n} o"
        if n < 1024 ** 2:   return f"{n/1024:.1f} Ko"
        return f"{n/1024**2:.2f} Mo"
