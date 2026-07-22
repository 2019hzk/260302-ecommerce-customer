import  uvicorn

from atguigu.config.config import  settings

if __name__ == '__main__':

    uvicorn.run(app="api.app:app",port=settings.app_port,host=settings.app_host)


