#!/bin/bash
set -e

# Di chuyển vào thư mục project
cd "$(dirname "$0")"

# Tạo môi trường ảo nếu chưa có
if [ ! -f ".venv/bin/python" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Cài thư viện nếu chưa cài hoặc requirements.txt thay đổi
if [ ! -f ".venv/.requirements_hash" ] || \
   [ "$(sha256sum requirements.txt | cut -d ' ' -f1)" != "$(cat .venv/.requirements_hash)" ]; then

    echo "Installing dependencies..."
    .venv/bin/python -m pip install -r requirements.txt

    sha256sum requirements.txt | cut -d ' ' -f1 > .venv/.requirements_hash
fi

# Chạy pipeline
echo "Starting YouTube Pipeline..."

.venv/bin/python main.py \
    --channel "@VieChannelOfficial" \
    --show "casimatna"

echo "Pipeline completed successfully!"