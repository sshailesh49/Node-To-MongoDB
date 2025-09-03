# Node.js + MongoDB Web App

## Run Locally

```bash
git clone https://github.com/yourname/node-mongo-app.git
cd node-mongo-app
docker-compose up -d --build
```

App will be available at:
- http://localhost:3000/healthz
- http://localhost:3000/api/users

### Example API Usage

Create a user:
```bash
curl -X POST http://localhost:3000/api/users   -H "Content-Type: application/json"   -d '{"name":"Alice","email":"alice@example.com"}'
```

List users:
```bash
curl http://localhost:3000/api/users
```