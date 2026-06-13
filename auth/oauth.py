import os
import streamlit as st
import requests
from urllib.parse import urlencode
from dotenv import load_dotenv

load_dotenv()


class GoogleOAuth:
    """Handles Google OAuth 2.0 authentication flow."""

    def __init__(self):
        self.client_id     = os.getenv("GOOGLE_CLIENT_ID", "")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")
        self.redirect_uri  = os.getenv("REDIRECT_URI", "")

    @property
    def is_configured(self) -> bool:
        return bool(
            self.client_id
            and self.client_id != "VOTRE_CLIENT_ID.apps.googleusercontent.com"
            and self.client_secret
            and self.redirect_uri
        )

    def is_authenticated(self) -> bool:
        return "user" in st.session_state

    def auth_url(self) -> str:
        return "https://accounts.google.com/o/oauth2/auth?" + urlencode({
            "client_id":     self.client_id,
            "redirect_uri":  self.redirect_uri,
            "response_type": "code",
            "scope":         "openid email profile",
            "prompt":        "select_account",
        })

    def _exchange_code(self, code: str) -> dict:
        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code":          code,
                "client_id":     self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri":  self.redirect_uri,
                "grant_type":    "authorization_code",
            },
            timeout=10,
        )
        return resp.json()

    def _get_userinfo(self, access_token: str) -> dict:
        resp = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
        )
        return resp.json()

    def handle_callback(self) -> None:
        """Process the ?code= redirect from Google."""
        qp = st.query_params
        if "code" not in qp or self.is_authenticated():
            return
        try:
            token = self._exchange_code(qp["code"])
            if "access_token" in token:
                st.session_state["user"] = self._get_userinfo(token["access_token"])
                st.query_params.clear()
                st.rerun()
            else:
                st.error(f"Connexion refusée : {token.get('error_description', token.get('error', '?'))}")
        except Exception as exc:
            st.error(f"Erreur OAuth : {exc}")

    def show_login_page(self) -> None:
        st.markdown("""
        <style>
        .login-wrap{min-height:80vh;display:flex;align-items:center;justify-content:center}
        .login-card{background:var(--surface);border:1px solid var(--border);border-radius:20px;
                    padding:3rem 2.5rem;max-width:420px;width:100%;text-align:center}
        .login-icon{font-size:3.2rem;margin-bottom:1rem}
        .login-title{font-family:'Syne',sans-serif;font-size:2.2rem;font-weight:800;margin:0 0 .4rem;
                     background:linear-gradient(135deg,#fff 25%,#6c63ff 65%,#ff6584);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
        .login-sub{color:var(--muted);font-size:.95rem;margin:0 0 2.2rem;line-height:1.6}
        .google-btn{display:inline-flex;align-items:center;gap:.65rem;background:#fff;color:#1a1a1a;
                    border-radius:10px;padding:.75rem 1.75rem;font-family:'Syne',sans-serif;font-weight:700;
                    font-size:.95rem;text-decoration:none;box-shadow:0 4px 24px rgba(0,0,0,.35);
                    transition:box-shadow .2s,transform .2s}
        .google-btn:hover{box-shadow:0 8px 32px rgba(0,0,0,.5);transform:translateY(-2px)}
        .login-note{color:var(--muted);font-size:.75rem;margin-top:1.8rem;line-height:1.5}
        </style>
        <div class="login-wrap">
          <div class="login-card">
            <div class="login-icon">📄</div>
            <div class="login-title">PDF Studio</div>
            <div class="login-sub">Suite complète d'outils PDF.<br>Connectez-vous pour accéder à l'application.</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if self.is_configured:
            col = st.columns([1, 2, 1])
            with col[1]:
                st.markdown(f"""
                <div style="text-align:center;margin-top:-6rem">
                  <a class="google-btn" href="{self.auth_url()}">
                    <svg width="20" height="20" viewBox="0 0 48 48">
                      <path fill="#FFC107" d="M43.6 20H24v8h11.3C33.9 33.4 29.4 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3 0 5.7 1.1 7.8 2.9l5.7-5.7C34.1 6.5 29.3 4.5 24 4.5 12.7 4.5 3.5 13.7 3.5 25S12.7 45.5 24 45.5c10.5 0 19.5-8.6 19.5-21 0-1.4-.1-2.7-.4-4z"/>
                      <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.5 16 19 13 24 13c3 0 5.7 1.1 7.8 2.9l5.7-5.7C34.1 6.5 29.3 4.5 24 4.5c-7.7 0-14.4 4.3-17.7 10.2z"/>
                      <path fill="#4CAF50" d="M24 45.5c5.2 0 9.9-1.9 13.5-5l-6.2-5.2C29.4 36.8 26.8 38 24 38c-5.4 0-9.9-3.6-11.4-8.5l-6.6 5.1C9.5 41.1 16.2 45.5 24 45.5z"/>
                      <path fill="#1565C0" d="M43.6 20H24v8h11.3c-.8 2.3-2.2 4.2-4.1 5.6l6.2 5.2c3.6-3.3 5.8-8.2 5.8-13.8 0-1.4-.1-2.7-.4-4z"/>
                    </svg>
                    Se connecter avec Google
                  </a>
                  <div class="login-note">Vos fichiers ne quittent jamais votre navigateur.</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Credentials Google non configurés.", icon="⚙️")
            st.caption("Renseignez vos valeurs dans `.env` :")
            st.code(
                'GOOGLE_CLIENT_ID     = "xxxx.apps.googleusercontent.com"\n'
                'GOOGLE_CLIENT_SECRET = "xxxx"\n'
                'REDIRECT_URI         = "http://localhost:8502"',
                language="bash",
            )

    def logout(self) -> None:
        st.session_state.pop("user", None)
        st.rerun()
