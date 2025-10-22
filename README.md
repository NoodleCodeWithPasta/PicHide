# PicHide

**PicHide** is a lightweight Python tool that hides secret messages or files inside images using the [`steghide`](https://steghide.sourceforge.net/) steganography utility.  
It provides a simple command-line interface and a fully containerized setup for reproducible, dependency-free use.

---

## Features

- Hide **text messages or files** inside JPEG/BMP images  
- Powered by `steghide` (real steganography, not just metadata tricks)  
- Non-interactive mode (no password prompts) → perfect for automation  
- Fully **Docker-ready** for reproducible environments  
- Supports optional compression (0–9)  
- Works on Linux, macOS, and Windows (via Docker)

---

## Installation

### 🔹 Option 1 - Local (Python ≥ 3.10)

1. Install `steghide`  
   - **Debian/Ubuntu:**  
     ```bash
     sudo apt install steghide
     ```  
   - **Arch Linux:**  
     ```bash
     git clone https://aur.archlinux.org/steghide.git
     ```

2. Clone the repository:
   ```bash
   git clone https://github.com/NoodleCodeWithPasta/PicHide.git
   cd PicHide
   ```

3. (Optional) install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the CLI:
   ```bash
   python3 hide.py --help
   ```

---

### 🔹 Option 2 - Docker (recommended)

Build the image once:
```bash
docker build -t pichide:latest .
```

Then use it directly:
```bash
docker run --rm -v "$PWD:/work" -w /work pichide:latest   embed --cover input.jpg --out stego.jpg --message "Top secret 🕵️" --compress 5
```

Extract a hidden message:
```bash
docker run --rm -v "$PWD:/work" -w /work pichide:latest   extract --stego stego.jpg --out message.txt
```

---

## Usage (Local Example)

### Embed a message
```bash
python3 hide.py embed   --cover /home/user/Pictures/input.jpg   --out /home/user/Pictures/stego.jpg   --message "The cake is a lie"   --passphrase ""   --compress 5   --force
```

### Extract the message
```bash
python3 hide.py extract   --stego /home/user/Pictures/stego.jpg   --out /home/user/Pictures/msg.txt   --passphrase ""
```

> If no `--passphrase` is provided, PicHide automatically uses an **empty password** (`-p ""`) to keep it fully non-interactive.

## Usage (Docker Example)

### Build Image
```bash
docker build -t steghide-tool:latest .
```

### Embed a message
```bash
docker run --rm -it \
  -e STEGHIDE_PASSPHRASE="myPassword" \
  -v "$PWD:/work" -w /work \
  steghide-tool:latest \
  embed --cover hellmo.jpg --out secret.jpg --message "Hellmo is dead" --compress 6 --force
```

### Extract the message
```bash
docker run --rm -it \
  -e STEGHIDE_PASSPHRASE="myPassword" \
  -v "$PWD:/work" -w /work \
  steghide-tool:latest \
  extract --stego secret.jpg --out msg.txt
```

> If no `--passphrase` is provided, PicHide automatically uses an **empty password** (`-p ""`) to keep it fully non-interactive.

---

## CLI Reference

| Command | Description |
|----------|--------------|
| `embed`  | Embed a message or file inside an image |
| `extract` | Extract a hidden message from a stego-image |

### Common options

| Option | Description |
|--------|--------------|
| `--cover` | Path to the carrier image (e.g. `.jpg`, `.bmp`) |
| `--out` | Output path for the stego image or extracted message |
| `--message` | Message as a string |
| `--message-file` | Read message from a file |
| `--passphrase` | Optional password (leave empty for none) |
| `--compress` | Compression level `0–9` |
| `--force` | Overwrite output if it already exists |

---

## Example Workflow

1. You have an image `hellmo.jpg` (creds to u/ParkingCake6!)
2. Hide a short message:
   ```bash
   python3 hide.py embed --cover hellmo.jpg --out secret.jpg --message "Hellmo is dead."
   ```
3. Send `secret.jpg` to someone  
4. They extract it:
   ```bash
   python3 hide.py extract --stego secret.jpg --out msg.txt
   cat msg.txt
   ```

---

## Notice

- Steganography hides **the presence** of data, not its encryption.  
  If secrecy is required, encrypt your message before embedding.  
- Use lossless image formats (e.g. `.bmp`) for best results.  
- Avoid recompressing images (e.g. via social media), as this can destroy hidden data.
