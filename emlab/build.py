import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from emlab.site import build_site  # noqa: E402


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build EMLab single-file HTML (offline).")
    p.add_argument(
        "--out",
        default=None,
        help="Output HTML path (default: repo_root/dist/emlab.html).",
    )
    p.add_argument(
        "--mode",
        default="release",
        choices=["release", "debug"],
        help="release=fully offline; debug=smaller html (may use CDN).",
    )
    p.add_argument(
        "--no-ct",
        action="store_true",
        help="Skip XCT/CT module (or avoid heavy CT deps).",
    )
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    out_path = Path(args.out) if args.out else (ROOT.parent / "dist" / "emlab.html")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    html = build_site(mode=args.mode, no_ct=args.no_ct)
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
