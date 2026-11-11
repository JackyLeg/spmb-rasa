# SPMB Rasa Open Source

Assistant virtual chatbot Penerimaan Mahasiswa Baru (SPMB) Universitas Trisakti berbasis Rasa Open Source 3.6.

## Setup & Deployment (Server)

```bash
mkdir spmb-rasa
cd spmb-rasa

git init
git remote add origin https://github.com/JackyLeg/spmb-rasa.git
git fetch origin
git reset --hard origin/main
git clean -fd

# Train
docker run --rm -v "$(pwd)":/app rasa/rasa:3.6.21-full train --domain domain/ --data data/

# Run
docker compose up -d
```

## Useful Commands

### Validate Data
```bash
docker run --rm -v "$(pwd)":/app rasa/rasa:3.6.21-full data validate --domain domain/ --data data/
```

### Train Model
```bash
docker run --rm -v "$(pwd)":/app rasa/rasa:3.6.21-full train --domain domain/ --data data/
```

### Run Interactive Shell
```bash
docker run -it -v "$(pwd)":/app rasa/rasa:3.6.21-full shell
```

### Docker Compose
```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f

# Stop services
docker compose down
```

### Cloudflare Tunnel (Optional)
```bash
cloudflared tunnel --url http://localhost:6005
```

