from __future__ import annotations

from html import escape
from typing import Iterable


def _help(help_text: str) -> str:
    if not help_text:
        return ""
    return f'<div class="help">{escape(help_text)}</div>'


def slider(
    *,
    cid: str,
    label: str,
    vmin: float,
    vmax: float,
    step: float,
    value: float,
    unit: str = "",
    help_text: str = "",
) -> str:
    return f"""
    <div class="control">
      <label for="{escape(cid)}">{escape(label)}</label>
      <div class="control-row">
        <input type="range" id="{escape(cid)}" min="{vmin}" max="{vmax}" step="{step}" value="{value}">
        <span class="value" id="{escape(cid)}-val"></span>
      </div>
      {_help(help_text)}
    </div>
    """.strip()


def number(
    *,
    cid: str,
    label: str,
    value: float,
    vmin: float | None = None,
    vmax: float | None = None,
    step: float | None = None,
    unit: str = "",
    help_text: str = "",
) -> str:
    attrs: list[str] = [f'id="{escape(cid)}"', f'value="{value}"', 'type="number"']
    if vmin is not None:
        attrs.append(f'min="{vmin}"')
    if vmax is not None:
        attrs.append(f'max="{vmax}"')
    if step is not None:
        attrs.append(f'step="{step}"')
    return f"""
    <div class="control">
      <label for="{escape(cid)}">{escape(label)}</label>
      <div class="control-row">
        <input {" ".join(attrs)}>
        <span class="value" id="{escape(cid)}-val">{escape(unit)}</span>
      </div>
      {_help(help_text)}
    </div>
    """.strip()


def select(
    *,
    cid: str,
    label: str,
    options: Iterable[tuple[str, str]],
    value: str,
    help_text: str = "",
) -> str:
    opts = "\n".join(
        f'<option value="{escape(v)}"{" selected" if v == value else ""}>{escape(t)}</option>'
        for v, t in options
    )
    return f"""
    <div class="control">
      <label for="{escape(cid)}">{escape(label)}</label>
      <select id="{escape(cid)}">
        {opts}
      </select>
      {_help(help_text)}
    </div>
    """.strip()


def buttons(buttons: Iterable[tuple[str, str, str]]) -> str:
    """
    buttons: (id, label, class_suffix)
    class_suffix: "", "primary", "danger"
    """
    btns = "\n".join(
        f'<button class="btn {escape(cls)}" id="{escape(cid)}" type="button">{escape(label)}</button>'
        for cid, label, cls in buttons
    )
    return f'<div class="btnrow">{btns}</div>'

