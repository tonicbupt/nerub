Nerub
=====

名字来源于 'Azjol Nerub', 诺森德下四通八达的蛛魔网络, 帮助 docker 构建 MacVLAN 网络.

需要本地有个 Redis, 配置还没有做.

用 Docker 跑:

`docker pull tonic/nerub`
`docker run -d --privileged --net=host -v /run/docker/plugins:/run/docker/plugins tonic/nerub`

直接跑:

`gunicorn -c gunicorn_config.py nerub.plugin:app`
