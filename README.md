## Docker

- 'docker build -t analytics_api -f Dockerfile.web .'
- 'docker run analytics_api'

## Docker run or stop

- 'docker compose up --watch'
- 'docker compose down' or 'docker compose down -v' (to remove volumes)
- 'docker compose run app /bin/bash' or 'docker compose run app python'