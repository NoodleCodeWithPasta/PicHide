#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

def check_steghide():
    if shutil.which("steghide") is None:
        print("Error: 'steghide' not installed or not in PATH.", file=sys.stderr)
        sys.exit(2)

def run(cmd):
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while running: {' '.join(cmd)}\nExit-Code: {e.returncode}", file=sys.stderr)
        sys.exit(e.returncode)

def embed_string(cover_path: Path, out_path: Path, message: str, passphrase: str | None, compress_level: int | None, force: bool):
    # write string in temp-file
    with tempfile.NamedTemporaryFile(prefix="msg_", suffix=".txt", delete=False) as tf:
        tf.write(message.encode("utf-8"))
        tf.flush()
        temp_msg_path = tf.name

    try:
        cmd = ["steghide", "embed",
               "-cf", str(cover_path),
               "-ef", temp_msg_path,
               "-sf", str(out_path)]
        if passphrase:
            cmd += ["-p", passphrase]
        else:
            cmd += ["-p", ""]  # set empty password to skip passphrase
        if compress_level is not None:
            # steghide: -z <level> (0..9)
            cmd += ["-z", str(compress_level)]
        if force:
            cmd += ["-f"]  # allow overwrite

        run(cmd)
        print(f"Successfully embedded in image: {out_path}")
    finally:
        try:
            os.remove(temp_msg_path)
        except OSError:
            pass

def extract(out_path: Path, extract_to: Path, passphrase: str | None):
    cmd = ["steghide", "extract", "-sf", str(out_path), "-xf", str(extract_to)]
    if passphrase:
        cmd += ["-p", passphrase]
    else:
        cmd += ["-p", ""]  # set empty password
    run(cmd)
    print(f"Extract message to: {extract_to}")

def valid_compress_level(val: str) -> int:
    try:
        i = int(val)
    except ValueError:
        raise argparse.ArgumentTypeError("Compressionlevel has to be a number (0-9).")
    if not (0 <= i <= 9):
        raise argparse.ArgumentTypeError("Compressionlevel has to be a number between 0 and 9.")
    return i

def main():
    parser = argparse.ArgumentParser(
        description="Hide a string in a picture wirh *steghide*."
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # embed
    p_embed = sub.add_parser("embed", help="Embed string in an image")
    p_embed.add_argument("--cover", "-c", required=True, type=Path, help="Path to target image (.jpg/.bmp)")
    p_embed.add_argument("--out", "-o", required=True, type=Path, help="Output image")
    p_embed.add_argument("--message", "-m", type=str, help="Message as string")
    p_embed.add_argument("--message-file", "-f", type=Path, help="Read message from file (alternative to --message)")
    p_embed.add_argument("--passphrase", "-p", type=str, default=os.getenv("STEGHIDE_PASSPHRASE", None),
                         help="Password (or via Env: STEGHIDE_PASSPHRASE)")
    p_embed.add_argument("--compress", "-z", type=valid_compress_level, default=None, help="Compressionlevel 0-9")
    p_embed.add_argument("--force", action="store_true", help="Overwrite outputfile if it already exists")

    # extract
    p_extract = sub.add_parser("extract", help="Extract message from stego image")
    p_extract.add_argument("--stego", "-s", required=True, type=Path, help="Path to stego image")
    p_extract.add_argument("--out", "-o", required=True, type=Path, help="Target file for message extraction (msg.txt)")
    p_extract.add_argument("--passphrase", "-p", type=str, default=os.getenv("STEGHIDE_PASSPHRASE", None),
                           help="Password (or via Env: STEGHIDE_PASSPHRASE)")

    args = parser.parse_args()
    check_steghide()

    if args.cmd == "embed":
        if (args.message is None) == (args.message_file is None):
            print("Choose ONE source for a message: --message OR --message-file.", file=sys.stderr)
            sys.exit(1)

        if args.message_file:
            if not args.message_file.exists():
                print(f"Message file not found: {args.message_file}", file=sys.stderr)
                sys.exit(1)
            message = args.message_file.read_text(encoding="utf-8")
        else:
            message = args.message

        if not args.cover.exists():
            print(f"Target image: {args.cover}", file=sys.stderr)
            sys.exit(1)

        # Zielordner anlegen falls nötig
        args.out.parent.mkdir(parents=True, exist_ok=True)
        embed_string(args.cover, args.out, message, args.passphrase, args.compress, args.force)

    elif args.cmd == "extract":
        if not args.stego.exists():
            print(f"Stego image not found: {args.stego}", file=sys.stderr)
            sys.exit(1)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        extract(args.stego, args.out, args.passphrase)

if __name__ == "__main__":
    main()
