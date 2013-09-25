
import json
import logging

from tornado.web import RequestHandler, HTTPError

import config
import template


class BaseHandler(RequestHandler):
    def render(self, template_name, content_type='text/html', **context):
        self.set_header('Content-Type', content_type)
        
        content = template.render(template_name, **context)
        self.finish(content)
    
    def finish_json(self, data={}):
        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps(data))


class MainHandler(BaseHandler):
    def get(self):
        self.render('main.html')


class ConfigHandler(BaseHandler):
    def get(self, camera_id=None, op=None):
        if camera_id is not None:
            camera_id = int(camera_id)
        
        if op == 'get':
            self.get_config(camera_id)
            
        elif op == 'list':
            self.list_cameras()
        
        else:
            raise HTTPError(400, 'unknown operation')
    
    def post(self, camera_id=None, op=None):
        if camera_id is not None:
            camera_id = int(camera_id)
        
        if op == 'set':
            self.set_config(camera_id)
        
        elif op == 'add':
            self.add_camera()
        
        elif op == 'rem':
            self.rem_camera(camera_id)
        
        else:
            raise HTTPError(400, 'unknown operation')
    
    def get_config(self, camera_id):
        if camera_id:
            logging.debug('getting config for camera %(id)s' % {'id': camera_id})
            
            camera_ids = config.get_camera_ids()
            if camera_id not in camera_ids:
                raise HTTPError(404, 'no such camera')
            
            self.finish_json(config.get_camera(camera_id))
            
        else:
            logging.debug('getting main config')
            
            self.finish_json(config.get_main())
    
    def set_config(self, camera_id):
        try:
            data = json.loads(self.request.body)
            
        except Exception as e:
            logging.error('could not decode json: %(msg)s' % {'msg': unicode(e)})
            
            raise
        
        if camera_id:
            logging.debug('setting config for camera %(id)s' % {'id': camera_id})
            
            camera_ids = config.get_camera_ids()
            if camera_id not in camera_ids:
                raise HTTPError(404, 'no such camera')
            
            config.set_camera(camera_id, data)

        else:
            logging.debug('setting main config')
            
            try:
                data = json.loads(self.request.body)
                
            except Exception as e:
                logging.error('could not decode json: %(msg)s' % {'msg': unicode(e)})
                
                raise
            
            config.set_main(data)
    
    def list_cameras(self):
        logging.debug('listing cameras')
        
        cameras = []
        for camera_id in config.get_camera_ids():
            data = config.get_camera(camera_id)
            data['@id'] = camera_id
            cameras.append(data)

        self.finish_json({'cameras': cameras})
    
    def add_camera(self):
        logging.debug('adding new camera')
        
        device = self.get_argument('device')
        camera_id, data = config.add_camera(device)
        
        data['@id'] = camera_id
        
        self.finish_json(data)
    
    def rem_camera(self, camera_id):
        logging.debug('removing camera %(id)s' % {'id': camera_id})
        
        config.rem_camera(camera_id)


class SnapshotHandler(BaseHandler):
    def get(self, camera_id, op, filename=None):
        if op == 'current':
            self.current()
            
        elif op == 'list':
            self.list(camera_id)
            
        elif op == 'download':
            self.download(filename)
        
        else:
            raise HTTPError(400, 'unknown operation')
    
    def current(self):
        pass
    
    def list(self, camera_id):
        logging.debug('listing snapshots for camera %(id)s' % {'id': camera_id})
    
    def download(self, camera_id, filename):
        logging.debug('downloading snapshot %(filename)s of camera %(id)s' % {
                'filename': filename, 'id': camera_id})


class MovieHandler(BaseHandler):
    def get(self, camera_id, op, filename=None):
        if op == 'list':
            self.list(camera_id)
            
        elif op == 'download':
            self.download(camera_id, filename)
        
        else:
            raise HTTPError(400, 'unknown operation')
    
    def list(self, camera_id):
        logging.debug('listing movies for camera %(id)s' % {'id': camera_id})
    
    def download(self, camera_id, filename):
        logging.debug('downloading movie %(filename)s of camera %(id)s' % {
                'filename': filename, 'id': camera_id})