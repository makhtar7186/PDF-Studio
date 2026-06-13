import io
import streamlit as st

from pdf_tools.processor import PDFProcessor
from pdf_tools.viewer    import PDFViewer
from ui.components       import fmt_size, file_card, stat_row, result_banner, section_label, card


class TabRenderer:
    """Renders all 14 functional tabs of PDF Studio."""

    def __init__(self, processor: PDFProcessor, viewer: PDFViewer):
        self.proc   = processor
        self.viewer = viewer

    def render_all(self) -> None:
        tabs = st.tabs([
            "🔍 Aperçu", "🔗 Fusion", "🗜️ Compression", "✂️ Découpage",
            "🗑️ Suppr. pages", "📤 Extraction", "🔄 Rotation", "🔀 Réordonner",
            "🔢 Numérotation", "📌 Insertion", "✂️ Rognage", "🔒 Protection",
            "💧 Filigrane", "✏️ Caviardage",
        ])
        renderers = [
            self._overview, self._merge, self._compress, self._split,
            self._delete, self._extract, self._rotate, self._reorder,
            self._number, self._insert, self._crop, self._protect,
            self._watermark, self._redact,
        ]
        for tab, renderer in zip(tabs, renderers):
            with tab:
                renderer()

    # ── 0. Aperçu ─────────────────────────────────────────────────────────────

    def _overview(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("🔍 Inspecter un document",
                 "Métadonnées, informations techniques et aperçu de toutes les pages.")
            f = st.file_uploader("PDF", type="pdf", key="ov_up", label_visibility="collapsed")
            if f:
                data = f.read(); f.seek(0)
                meta = self.proc.metadata(data)
                stat_row(
                    ("Pages",   str(meta["pages"])),
                    ("Taille",  fmt_size(len(data))),
                    ("Format",  meta["sizes"]),
                    ("Chiffré", "Oui" if meta["encrypted"] else "Non"),
                )
                file_card(f.name, len(data), meta["pages"])
        with c2:
            if f:
                section_label("Métadonnées")
                fields = [("Titre", meta["title"]), ("Auteur", meta["author"]),
                          ("Créateur", meta["creator"]), ("Producteur", meta["producer"])]
                st.markdown(
                    "".join(
                        f'<div class="meta-row"><div class="meta-key">{k}</div>'
                        f'<div class="meta-val">{v}</div></div>'
                        for k, v in fields
                    ),
                    unsafe_allow_html=True,
                )
        if f:
            section_label("Toutes les pages")
            with st.spinner("Génération des miniatures…"):
                self.viewer.show_grid(data, key="overview")

    # ── 1. Fusion ─────────────────────────────────────────────────────────────

    def _merge(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("📂 Fichiers à fusionner",
                 "Ordre d'import = ordre de fusion. Minimum 2 fichiers.")
            files = st.file_uploader("PDF", type="pdf", accept_multiple_files=True,
                                     key="m_up", label_visibility="collapsed")
            if files:
                total_p = 0
                for f in files:
                    d = f.read(); f.seek(0)
                    pg = self.proc.page_count(d); total_p += pg
                    file_card(f.name, f.size, pg)
                stat_row(
                    ("Fichiers", str(len(files))),
                    ("Pages",   str(total_p)),
                    ("Taille",  fmt_size(sum(f.size for f in files))),
                )
        with c2:
            card("⚙️ Options")
            name = st.text_input("Nom du fichier de sortie", value="fusionné", key="m_name")
            if st.button("🔗 Fusionner", key="m_btn"):
                if not files or len(files) < 2:
                    st.error("Sélectionnez au moins 2 fichiers.")
                else:
                    with st.spinner("Fusion…"):
                        try:
                            result = self.proc.merge(files)
                            st.session_state.update({
                                "merge_result": result,
                                "merge_fn":     (name.strip() or "fusionné") + ".pdf",
                                "merge_pg":     self.proc.page_count(result),
                            })
                        except Exception as e:
                            st.error(f"Erreur : {e}")
                            st.session_state.pop("merge_result", None)

        if st.session_state.get("merge_result"):
            r = st.session_state["merge_result"]
            result_banner(st.session_state["merge_pg"], f"pages · {fmt_size(len(r))}")
            st.download_button("⬇️ Télécharger", r, st.session_state["merge_fn"],
                               "application/pdf", key="m_dl")
            self.viewer.show_preview(r, key="merge", title="Aperçu — Document fusionné")
            with st.expander("🗂️ Vue d'ensemble"):
                self.viewer.show_grid(r, key="merge_grid")

    # ── 2. Compression ────────────────────────────────────────────────────────

    def _compress(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("📂 Fichier à compresser")
            cf = st.file_uploader("PDF", type="pdf", key="c_up", label_visibility="collapsed")
            if cf:
                d = cf.read(); cf.seek(0)
                file_card(cf.name, cf.size, self.proc.page_count(d))
        with c2:
            card("⚙️ Niveau de compression")
            level_map = {
                "🟢 Légère (qualité max, métadonnées supprimées)": 1,
                "🟡 Modérée (flux + images à 75 %)":               2,
                "🔴 Agressive (images à 45 %, archivage)":         3,
            }
            label = st.selectbox("Niveau", list(level_map.keys()), index=1,
                                 key="c_lv", label_visibility="collapsed")
            name  = st.text_input("Nom de sortie", value="compressé", key="c_name")
            if st.button("🗜️ Compresser", key="c_btn"):
                if not cf:
                    st.error("Sélectionnez un fichier.")
                else:
                    with st.spinner("Compression…"):
                        try:
                            cf.seek(0); orig = cf.read()
                            res   = self.proc.compress(orig, level_map[label])
                            ratio = (1 - len(res) / len(orig)) * 100
                            st.session_state.update({
                                "compress_result": res,
                                "compress_fn":     (name.strip() or "compressé") + ".pdf",
                                "compress_ratio":  ratio,
                                "compress_orig":   len(orig),
                            })
                        except Exception as e:
                            st.error(f"Erreur : {e}")
                            st.session_state.pop("compress_result", None)

        if st.session_state.get("compress_result"):
            r     = st.session_state["compress_result"]
            ratio = st.session_state["compress_ratio"]
            orig  = st.session_state["compress_orig"]
            color = "var(--accent3)" if ratio > 0 else "var(--accent2)"
            lbl   = (f"réduction · {fmt_size(orig)} → {fmt_size(len(r))}" if ratio > 0
                     else f"taille augmentée (PDF déjà optimisé) · {fmt_size(orig)} → {fmt_size(len(r))}")
            st.markdown(
                f'<div class="result-banner">'
                f'<span class="big-num" style="color:{color}">{ratio:+.1f}%</span>'
                f'<div class="label">{lbl}</div></div>',
                unsafe_allow_html=True,
            )
            pct = max(0, min(100, ratio))
            st.markdown(
                f'<div class="progress-wrap"><div class="progress-fill" style="width:{pct}%"></div></div>',
                unsafe_allow_html=True,
            )
            st.download_button("⬇️ Télécharger", r, st.session_state["compress_fn"],
                               "application/pdf", key="c_dl")
            self.viewer.show_preview(r, key="compress", title="Aperçu — Document compressé")

    # ── 3. Découpage ──────────────────────────────────────────────────────────

    def _split(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("✂️ Fichier à découper")
            sf = st.file_uploader("PDF", type="pdf", key="s_up", label_visibility="collapsed")
            if sf:
                sd = sf.read(); sf.seek(0)
                n  = self.proc.page_count(sd)
                file_card(sf.name, sf.size, n)
                st.markdown(f'<div class="stat-chip" style="margin-top:.5rem">📄 <span>{n} pages</span></div>',
                            unsafe_allow_html=True)
        with c2:
            card("⚙️ Mode de découpage")
            mode = st.selectbox("Mode",
                                ["Par plages personnalisées", "Toutes les N pages", "Page par page"],
                                key="s_mode", label_visibility="collapsed")
            ranges_txt, n_per = "", 10
            if mode == "Par plages personnalisées":
                st.caption("Ex : `1-5, 6-10, 15-20`")
                ranges_txt = st.text_input("Plages", placeholder="1-5, 6-12, 13-20", key="s_ranges")
            elif mode == "Toutes les N pages":
                n_per = st.number_input("Pages par partie", min_value=1, value=10, key="s_n")
            prefix = st.text_input("Préfixe de nom", value="partie", key="s_name")

            if st.button("✂️ Découper", key="s_btn"):
                if not sf:
                    st.error("Sélectionnez un fichier.")
                else:
                    sf.seek(0); sd = sf.read()
                    n_pages = self.proc.page_count(sd)
                    ranges  = self._build_split_ranges(mode, ranges_txt, n_per, n_pages)
                    if not ranges:
                        st.error("Aucune plage valide.")
                    else:
                        with st.spinner("Découpage…"):
                            pfx = prefix.strip() or "partie"
                            if len(ranges) == 1:
                                parts = self.proc.split(sd, ranges)
                                st.session_state["split_single"] = parts[0]
                                st.session_state["split_fn"]     = f"{pfx}_1.pdf"
                                st.session_state.pop("split_zip", None)
                            else:
                                zb = self.proc.split_to_zip(sd, ranges, pfx)
                                st.session_state.update({
                                    "split_zip":    zb,
                                    "split_zip_fn": f"{pfx}.zip",
                                    "split_count":  len(ranges),
                                })
                                st.session_state.pop("split_single", None)

        if st.session_state.get("split_single"):
            st.download_button("⬇️ Télécharger", st.session_state["split_single"],
                               st.session_state["split_fn"], "application/pdf", key="s_dl0")
            self.viewer.show_preview(st.session_state["split_single"],
                                     key="split", title="Aperçu — Partie découpée")
        elif st.session_state.get("split_zip"):
            st.success(f"✅ {st.session_state['split_count']} fichiers créés")
            st.download_button("⬇️ Télécharger le ZIP", st.session_state["split_zip"],
                               st.session_state["split_zip_fn"], "application/zip", key="s_dlz")

    @staticmethod
    def _build_split_ranges(mode: str, ranges_txt: str, n_per: int, n_pages: int) -> list:
        ranges = []
        if mode == "Par plages personnalisées":
            for part in ranges_txt.split(","):
                part = part.strip()
                if "-" in part:
                    a, b = part.split("-", 1)
                    try:
                        ranges.append((int(a.strip()) - 1, int(b.strip()) - 1))
                    except ValueError:
                        pass
        elif mode == "Toutes les N pages":
            i = 0
            while i < n_pages:
                ranges.append((i, min(i + int(n_per) - 1, n_pages - 1)))
                i += int(n_per)
        else:
            ranges = [(i, i) for i in range(n_pages)]
        return ranges

    # ── 4. Suppression de pages ───────────────────────────────────────────────

    def _delete(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("🗑️ Fichier source")
            df = st.file_uploader("PDF", type="pdf", key="d_up", label_visibility="collapsed")
            if df:
                dd = df.read(); df.seek(0)
                file_card(df.name, df.size, self.proc.page_count(dd))
        with c2:
            card("⚙️ Pages à supprimer")
            st.caption("Ex : `1, 3, 5-8`")
            del_txt = st.text_input("Pages", placeholder="2, 4, 7-10", key="d_pages")
            name    = st.text_input("Nom de sortie", value="sans_pages", key="d_name")
            if st.button("🗑️ Supprimer les pages", key="d_btn"):
                if not df:
                    st.error("Sélectionnez un fichier.")
                else:
                    df.seek(0); dd = df.read()
                    n      = self.proc.page_count(dd)
                    to_del = self.proc.parse_page_ranges(del_txt, n)
                    if not to_del:
                        st.error("Aucune page valide spécifiée.")
                    elif len(to_del) >= n:
                        st.error("Vous ne pouvez pas supprimer toutes les pages.")
                    else:
                        with st.spinner("Suppression…"):
                            res = self.proc.delete_pages(dd, to_del)
                            st.session_state.update({
                                "delete_result":  res,
                                "delete_fn":      (name.strip() or "sans_pages") + ".pdf",
                                "delete_pg_out":  self.proc.page_count(res),
                                "delete_deleted": len(to_del),
                            })

        if st.session_state.get("delete_result"):
            r = st.session_state["delete_result"]
            result_banner(st.session_state["delete_pg_out"],
                          f"pages restantes · {st.session_state['delete_deleted']} supprimées")
            st.download_button("⬇️ Télécharger", r, st.session_state["delete_fn"],
                               "application/pdf", key="d_dl")
            self.viewer.show_preview(r, key="delete", title="Aperçu — Pages supprimées")

    # ── 5. Extraction ─────────────────────────────────────────────────────────

    def _extract(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("📤 Fichier source")
            ef = st.file_uploader("PDF", type="pdf", key="e_up", label_visibility="collapsed")
            if ef:
                ed = ef.read(); ef.seek(0)
                file_card(ef.name, ef.size, self.proc.page_count(ed))
        with c2:
            card("⚙️ Pages à extraire")
            st.caption("Ex : `1, 5-10, 15`")
            ext_txt = st.text_input("Pages", placeholder="1, 5-10, 15", key="e_pages")
            name    = st.text_input("Nom de sortie", value="extrait", key="e_name")
            if st.button("📤 Extraire", key="e_btn"):
                if not ef:
                    st.error("Sélectionnez un fichier.")
                else:
                    ef.seek(0); ed = ef.read()
                    to_keep = self.proc.parse_page_ranges(ext_txt, self.proc.page_count(ed))
                    if not to_keep:
                        st.error("Aucune page valide.")
                    else:
                        with st.spinner("Extraction…"):
                            res = self.proc.extract_pages(ed, to_keep)
                            st.session_state.update({
                                "extract_result": res,
                                "extract_fn":     (name.strip() or "extrait") + ".pdf",
                                "extract_pg_out": self.proc.page_count(res),
                            })

        if st.session_state.get("extract_result"):
            r = st.session_state["extract_result"]
            result_banner(st.session_state["extract_pg_out"],
                          f"pages extraites · {fmt_size(len(r))}")
            st.download_button("⬇️ Télécharger", r, st.session_state["extract_fn"],
                               "application/pdf", key="e_dl")
            self.viewer.show_preview(r, key="extract", title="Aperçu — Pages extraites")
            with st.expander("🗂️ Vue d'ensemble"):
                self.viewer.show_grid(r, key="extract_grid")

    # ── 6. Rotation ───────────────────────────────────────────────────────────

    def _rotate(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("🔄 Fichier à pivoter")
            rf = st.file_uploader("PDF", type="pdf", key="r_up", label_visibility="collapsed")
            if rf:
                rd = rf.read(); rf.seek(0)
                file_card(rf.name, rf.size, self.proc.page_count(rd))
        with c2:
            card("⚙️ Options de rotation")
            rot_map   = {"90° (horaire)": 90, "180°": 180, "270° (anti-horaire)": 270}
            rot_label = st.selectbox("Angle", list(rot_map.keys()), key="r_angle")
            rot_all   = st.checkbox("Appliquer à toutes les pages", value=True, key="r_all")
            pages_txt = ""
            if not rot_all:
                pages_txt = st.text_input("Pages spécifiques", placeholder="1,3,5-8", key="r_pages")
            name = st.text_input("Nom de sortie", value="pivoté", key="r_name")
            if st.button("🔄 Pivoter", key="r_btn"):
                if not rf:
                    st.error("Sélectionnez un fichier.")
                else:
                    rf.seek(0); rd = rf.read()
                    sel   = None if rot_all else self.proc.parse_page_ranges(pages_txt, self.proc.page_count(rd))
                    angle = rot_map[rot_label]
                    with st.spinner("Rotation…"):
                        res = self.proc.rotate_pages(rd, angle, sel)
                        st.session_state.update({
                            "rotate_result": res,
                            "rotate_fn":     (name.strip() or "pivoté") + ".pdf",
                            "rotate_angle":  angle,
                        })

        if st.session_state.get("rotate_result"):
            r = st.session_state["rotate_result"]
            st.success(f"✅ Rotation {st.session_state['rotate_angle']}° appliquée")
            st.download_button("⬇️ Télécharger", r, st.session_state["rotate_fn"],
                               "application/pdf", key="r_dl")
            self.viewer.show_preview(r, key="rotate", title="Aperçu — Document pivoté")

    # ── 7. Réordonner ─────────────────────────────────────────────────────────

    def _reorder(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("🔀 Fichier à réordonner")
            orf = st.file_uploader("PDF", type="pdf", key="o_up", label_visibility="collapsed")
            if orf:
                od = orf.read(); orf.seek(0)
                n  = self.proc.page_count(od)
                file_card(orf.name, orf.size, n)
                st.markdown(f'<div class="stat-chip" style="margin-top:.5rem">📄 Pages : <span>1 → {n}</span></div>',
                            unsafe_allow_html=True)
                with st.expander("🗂️ Ordre actuel"):
                    with st.spinner("Chargement…"):
                        self.viewer.show_grid(od, key="reorder_before")
        with c2:
            card("⚙️ Nouvel ordre")
            st.caption("Ex : `3,1,2,5,4` pour 5 pages")
            order_txt = st.text_input("Nouvel ordre", placeholder="3, 1, 2, 5, 4", key="o_order")
            name      = st.text_input("Nom de sortie", value="réordonné", key="o_name")
            if st.button("🔀 Réordonner", key="o_btn"):
                if not orf:
                    st.error("Sélectionnez un fichier.")
                else:
                    orf.seek(0); od = orf.read()
                    n = self.proc.page_count(od)
                    try:
                        new_order = [int(x.strip()) - 1 for x in order_txt.split(",") if x.strip()]
                        invalid   = [i for i in new_order if not (0 <= i < n)]
                        if invalid:
                            st.error(f"Pages invalides : {[i+1 for i in invalid]}")
                        else:
                            with st.spinner("Réorganisation…"):
                                res = self.proc.reorder_pages(od, new_order)
                                st.session_state.update({
                                    "reorder_result": res,
                                    "reorder_fn":     (name.strip() or "réordonné") + ".pdf",
                                    "reorder_count":  len(new_order),
                                })
                    except Exception as ex:
                        st.error(f"Erreur de format : {ex}")

        if st.session_state.get("reorder_result"):
            r = st.session_state["reorder_result"]
            st.success(f"✅ {st.session_state['reorder_count']} pages réordonnées")
            st.download_button("⬇️ Télécharger", r, st.session_state["reorder_fn"],
                               "application/pdf", key="o_dl")
            self.viewer.show_preview(r, key="reorder", title="Aperçu — Document réordonné")
            with st.expander("🗂️ Nouvel ordre des pages"):
                self.viewer.show_grid(r, key="reorder_after")

    # ── 8. Numérotation ───────────────────────────────────────────────────────

    def _number(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("🔢 Fichier à numéroter")
            nf = st.file_uploader("PDF", type="pdf", key="n_up", label_visibility="collapsed")
            if nf:
                nd = nf.read(); nf.seek(0)
                file_card(nf.name, nf.size, self.proc.page_count(nd))
        with c2:
            card("⚙️ Options de numérotation")
            pos_map = {
                "Bas centre":   "bottom-center", "Bas droite":    "bottom-right",
                "Bas gauche":   "bottom-left",   "Haut centre":   "top-center",
                "Haut droite":  "top-right",      "Haut gauche":   "top-left",
            }
            pos    = st.selectbox("Position", list(pos_map.keys()), key="n_pos")
            start  = st.number_input("Numéro de départ", min_value=1, value=1, key="n_start")
            prefix = st.text_input("Préfixe", placeholder="Page ", value="", key="n_prefix")
            size   = st.slider("Taille de la police", 7, 20, 10, key="n_size")
            name   = st.text_input("Nom de sortie", value="numéroté", key="n_name")
            if st.button("🔢 Numéroter", key="n_btn"):
                if not nf:
                    st.error("Sélectionnez un fichier.")
                else:
                    nf.seek(0); nd = nf.read()
                    with st.spinner("Ajout des numéros…"):
                        try:
                            res = self.proc.number_pages(nd, pos_map[pos], int(start), prefix, size)
                            st.session_state.update({
                                "number_result": res,
                                "number_fn":     (name.strip() or "numéroté") + ".pdf",
                            })
                        except Exception as ex:
                            st.error(f"Erreur : {ex}")
                            st.session_state.pop("number_result", None)

        if st.session_state.get("number_result"):
            r = st.session_state["number_result"]
            st.success("✅ Pages numérotées")
            st.download_button("⬇️ Télécharger", r, st.session_state["number_fn"],
                               "application/pdf", key="n_dl")
            self.viewer.show_preview(r, key="number", title="Aperçu — Pages numérotées")

    # ── 9. Insertion ──────────────────────────────────────────────────────────

    def _insert(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("📌 Document de base")
            f1 = st.file_uploader("Document principal", type="pdf",
                                  key="i_base", label_visibility="collapsed")
            st.markdown('<div class="card-title" style="margin-top:.8rem">📎 Pages à insérer</div>',
                        unsafe_allow_html=True)
            f2 = st.file_uploader("Pages à insérer", type="pdf",
                                  key="i_insert", label_visibility="collapsed")
            if f1 and f2:
                d1 = f1.read(); f1.seek(0)
                d2 = f2.read(); f2.seek(0)
                file_card(f1.name, f1.size, self.proc.page_count(d1))
                file_card(f2.name, f2.size, self.proc.page_count(d2))
        with c2:
            card("⚙️ Position d'insertion")
            st.caption("0 = début, N = après la page N")
            pos  = st.number_input("Insérer après la page N°", min_value=0, value=0, key="i_pos")
            name = st.text_input("Nom de sortie", value="avec_insertion", key="i_name")
            if st.button("📌 Insérer", key="i_btn"):
                if not f1 or not f2:
                    st.error("Sélectionnez les deux fichiers.")
                else:
                    f1.seek(0); f2.seek(0)
                    d1 = f1.read(); d2 = f2.read()
                    with st.spinner("Insertion…"):
                        try:
                            res = self.proc.insert_pages(d1, d2, int(pos) - 1)
                            st.session_state.update({
                                "insert_result": res,
                                "insert_fn":     (name.strip() or "avec_insertion") + ".pdf",
                                "insert_pg_out": self.proc.page_count(res),
                            })
                        except Exception as ex:
                            st.error(f"Erreur : {ex}")
                            st.session_state.pop("insert_result", None)

        if st.session_state.get("insert_result"):
            r = st.session_state["insert_result"]
            result_banner(st.session_state["insert_pg_out"], "pages au total après insertion")
            st.download_button("⬇️ Télécharger", r, st.session_state["insert_fn"],
                               "application/pdf", key="i_dl")
            self.viewer.show_preview(r, key="insert", title="Aperçu — Document avec insertion")

    # ── 10. Rognage ───────────────────────────────────────────────────────────

    def _crop(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("✂️ Fichier à rogner")
            cf = st.file_uploader("PDF", type="pdf", key="cr_up", label_visibility="collapsed")
            if cf:
                cd = cf.read(); cf.seek(0)
                file_card(cf.name, cf.size, self.proc.page_count(cd))
        with c2:
            card("⚙️ Marges à supprimer (%)",
                 "Pourcentage à couper de chaque bord (0–40 %)")
            left   = st.slider("Bord gauche (%)",    0, 40, 0, key="cr_l") / 100
            right  = st.slider("Bord droit (%)",     0, 40, 0, key="cr_r") / 100
            top    = st.slider("Bord supérieur (%)", 0, 40, 0, key="cr_t") / 100
            bottom = st.slider("Bord inférieur (%)", 0, 40, 0, key="cr_b") / 100
            name   = st.text_input("Nom de sortie", value="rogné", key="cr_name")
            if st.button("✂️ Rogner", key="cr_btn"):
                if not cf:
                    st.error("Sélectionnez un fichier.")
                else:
                    cf.seek(0); cd = cf.read()
                    with st.spinner("Rognage…"):
                        try:
                            res = self.proc.crop_pages(cd, left, bottom, right, top)
                            st.session_state.update({
                                "crop_result": res,
                                "crop_fn":     (name.strip() or "rogné") + ".pdf",
                            })
                        except Exception as ex:
                            st.error(f"Erreur : {ex}")
                            st.session_state.pop("crop_result", None)

        if st.session_state.get("crop_result"):
            r = st.session_state["crop_result"]
            st.success("✅ Pages rognées")
            st.download_button("⬇️ Télécharger", r, st.session_state["crop_fn"],
                               "application/pdf", key="cr_dl")
            self.viewer.show_preview(r, key="crop", title="Aperçu — Document rogné")

    # ── 11. Protection ────────────────────────────────────────────────────────

    def _protect(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("🔒 Fichier à protéger")
            pf = st.file_uploader("PDF", type="pdf", key="p_up", label_visibility="collapsed")
            if pf:
                pd_ = pf.read(); pf.seek(0)
                file_card(pf.name, pf.size, self.proc.page_count(pd_))
        with c2:
            card("⚙️ Mot de passe")
            pw1  = st.text_input("Mot de passe d'ouverture", type="password", key="p_pw1")
            pw2  = st.text_input("Confirmer le mot de passe", type="password", key="p_pw2")
            name = st.text_input("Nom de sortie", value="protégé", key="p_name")
            if st.button("🔒 Protéger", key="p_btn"):
                if not pf:
                    st.error("Sélectionnez un fichier.")
                elif not pw1:
                    st.error("Entrez un mot de passe.")
                elif pw1 != pw2:
                    st.error("Les mots de passe ne correspondent pas.")
                else:
                    pf.seek(0); pd_ = pf.read()
                    with st.spinner("Chiffrement…"):
                        try:
                            res = self.proc.protect(pd_, pw1)
                            st.session_state.update({
                                "protect_result": res,
                                "protect_fn":     (name.strip() or "protégé") + ".pdf",
                            })
                        except Exception as ex:
                            st.error(f"Erreur : {ex}")
                            st.session_state.pop("protect_result", None)

        if st.session_state.get("protect_result"):
            r = st.session_state["protect_result"]
            st.success("✅ PDF protégé — aperçu non disponible pour les fichiers chiffrés")
            st.download_button("⬇️ Télécharger", r, st.session_state["protect_fn"],
                               "application/pdf", key="p_dl")

    # ── 12. Filigrane ─────────────────────────────────────────────────────────

    def _watermark(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("💧 Fichier à filigraner")
            wf = st.file_uploader("PDF", type="pdf", key="w_up", label_visibility="collapsed")
            if wf:
                wd = wf.read(); wf.seek(0)
                file_card(wf.name, wf.size, self.proc.page_count(wd))
        with c2:
            card("⚙️ Options du filigrane")
            text    = st.text_input("Texte", value="CONFIDENTIEL", key="w_text")
            opacity = st.slider("Opacité (%)", 5, 60, 15, key="w_opacity") / 100
            angle   = st.slider("Angle (°)", 0, 90, 45, key="w_angle")
            size    = st.slider("Taille de la police", 20, 120, 50, key="w_size")
            name    = st.text_input("Nom de sortie", value="filigrané", key="w_name")
            if st.button("💧 Appliquer le filigrane", key="w_btn"):
                if not wf:
                    st.error("Sélectionnez un fichier.")
                elif not text.strip():
                    st.error("Entrez un texte de filigrane.")
                else:
                    wf.seek(0); wd = wf.read()
                    with st.spinner("Application du filigrane…"):
                        try:
                            res = self.proc.add_watermark(wd, text.strip(), opacity, angle, size)
                            st.session_state.update({
                                "watermark_result": res,
                                "watermark_fn":     (name.strip() or "filigrané") + ".pdf",
                            })
                        except Exception as ex:
                            st.error(f"Erreur : {ex}")
                            st.session_state.pop("watermark_result", None)

        if st.session_state.get("watermark_result"):
            r = st.session_state["watermark_result"]
            st.success("✅ Filigrane appliqué à toutes les pages")
            st.download_button("⬇️ Télécharger", r, st.session_state["watermark_fn"],
                               "application/pdf", key="w_dl")
            self.viewer.show_preview(r, key="watermark", title="Aperçu — Document filigrané")

    # ── 13. Caviardage ────────────────────────────────────────────────────────

    def _redact(self) -> None:
        c1, c2 = st.columns(2, gap="large")
        with c1:
            card("✏️ Fichier à caviarder")
            rf = st.file_uploader("PDF", type="pdf", key="red_up", label_visibility="collapsed")
            if rf:
                rd = rf.read(); rf.seek(0)
                file_card(rf.name, rf.size, self.proc.page_count(rd))
        with c2:
            card("⚙️ Termes à caviarder",
                 "Un terme par ligne. Les occurrences seront remplacées par des blocs noirs permanents.")
            terms_txt = st.text_area("Termes", placeholder="Nom Prénom\nNuméro\nadresse@email.com",
                                     height=140, key="red_terms")
            name = st.text_input("Nom de sortie", value="caviardé", key="red_name")
            if st.button("✏️ Caviarder", key="red_btn"):
                if not rf:
                    st.error("Sélectionnez un fichier.")
                elif not terms_txt.strip():
                    st.error("Entrez au moins un terme.")
                else:
                    rf.seek(0); rd = rf.read()
                    terms = [t for t in terms_txt.splitlines() if t.strip()]
                    with st.spinner("Caviardage en cours…"):
                        try:
                            res, count = self.proc.redact(rd, terms)
                            if count == 0:
                                st.warning("⚠️ Aucune occurrence trouvée (sensible à la casse).")
                            else:
                                st.session_state.update({
                                    "redact_result": res,
                                    "redact_fn":     (name.strip() or "caviardé") + ".pdf",
                                    "redact_count":  count,
                                })
                        except Exception as ex:
                            st.error(f"Erreur : {ex}")
                            st.session_state.pop("redact_result", None)

        if st.session_state.get("redact_result"):
            r = st.session_state["redact_result"]
            c = st.session_state["redact_count"]
            result_banner(c, f'occurrence{"s" if c > 1 else ""} caviardée{"s" if c > 1 else ""}')
            st.download_button("⬇️ Télécharger", r, st.session_state["redact_fn"],
                               "application/pdf", key="red_dl")
            self.viewer.show_preview(r, key="redact", title="Aperçu — Document caviardé")
