Nerub
=====

名字来源于 'Azjol Nerub', 诺森德下四通八达的蛛魔网络, 帮助 docker 构建 MacVLAN 网络.

用 Docker 跑:

`docker pull tonic/nerub`

`docker run -d --privileged -e REDIS_HOST=127.0.0.1 -e REDIS_PORT=6379 --net=host -v /run/docker/plugins:/run/docker/plugins tonic/nerub`

直接跑:

```
export REDIS_HOST=127.0.0.1
export REDIS_PORT=6379
gunicorn -c gunicorn_config.py nerub.plugin:app
```
