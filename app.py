import streamlit as st

from auth.oauth      import GoogleOAuth
from pdf_tools.processor import PDFProcessor
from pdf_tools.viewer    import PDFViewer
from ui.styles       import setup_page, inject_css
from ui.tabs         import TabRenderer
from ui.components   import fmt_size


class PDFStudioApp:
    """Main application class - wires up auth, PDF engine and UI."""

    def __init__(self):
        self.oauth    = GoogleOAuth()
        self.proc     = PDFProcessor()
        self.viewer   = PDFViewer()
        self.renderer = TabRenderer(self.proc, self.viewer)

    def run(self) -> None:
        setup_page()
        inject_css()

        self.oauth.handle_callback()

        if not self.oauth.is_authenticated():
            self.oauth.show_login_page()
            st.stop()

        self._render_user_badge()
        self._render_hero()
        self.renderer.render_all()
        self._render_footer()

    def _render_user_badge(self) -> None:
        user   = st.session_state["user"]
        avatar = user.get("picture", "")
        name   = user.get("name", user.get("email", "Utilisateur"))
        email  = user.get("email", "")

        cols = st.columns([7, 1])
        with cols[1]:
            img_html = (
                f"<img src='{avatar}' style='width:28px;height:28px;"
                f"border-radius:50%;vertical-align:middle;margin-right:.4rem'>"
                if avatar else ""
            )
            st.markdown(
                f'<div style="text-align:right;padding:.4rem 0">'
                f'{img_html}'
                f'<span style="font-size:.8rem;color:var(--muted);vertical-align:middle">{name}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Déconnexion", key="_logout", help=email):
                self.oauth.logout()

    @staticmethod
    def _render_hero() -> None:
        st.markdown("""
        <div class="hero">
          <h1>PDF Studio</h1>
          <p>Suite complète d'outils PDF - 100 % local, aucun fichier envoyé sur un serveur</p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def _render_footer() -> None:
        st.markdown(
            '<div style="text-align:center;margin-top:3rem;color:#252535;font-size:.75rem;'
            'font-family:DM Sans,sans-serif">'
            'PDF Studio · Traitement 100 % local - aucun fichier transmis sur un serveur'
            '</div>',
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    PDFStudioApp().run()
