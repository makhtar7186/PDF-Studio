import streamlit as st


def fmt_size(n: int) -> str:
    if n < 1024:       return f"{n} o"
    if n < 1024 ** 2:  return f"{n/1024:.1f} Ko"
    return f"{n/1024**2:.2f} Mo"


def file_card(name: str, size_bytes: int, pages: int = None) -> None:
    extra = f" · {pages}p" if pages else ""
    st.markdown(f"""
    <div class="file-item">
      <div class="file-icon">PDF</div>
      <div class="file-name">{name}</div>
      <div class="file-size">{fmt_size(size_bytes)}{extra}</div>
    </div>""", unsafe_allow_html=True)


def stat_row(*chips: tuple) -> None:
    """chips: list of (label, value) tuples."""
    html = "".join(
        f'<div class="stat-chip">{label} : <span>{value}</span></div>'
        for label, value in chips
    )
    st.markdown(f'<div class="stat-row">{html}</div>', unsafe_allow_html=True)


def result_banner(big_number, label: str) -> None:
    st.markdown(
        f'<div class="result-banner">'
        f'<span class="big-num">{big_number}</span>'
        f'<div class="label">{label}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(f'<div class="section-label">{text}</div>', unsafe_allow_html=True)


def card(title: str, subtitle: str = "") -> None:
    sub_html = f'<div class="card-sub">{subtitle}</div>' if subtitle else ""
    st.markdown(
        f'<div class="card"><div class="card-title">{title}</div>{sub_html}</div>',
        unsafe_allow_html=True,
    )
