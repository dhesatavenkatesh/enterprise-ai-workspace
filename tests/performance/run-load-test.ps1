locust `
  -f tests\performance\locustfile.py `
  --host=http://127.0.0.1:8000 `
  --headless `
  --users 20 `
  --spawn-rate 2 `
  --run-time 1m `
  --csv=tests\performance\results
