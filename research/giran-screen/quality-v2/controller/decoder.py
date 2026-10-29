"""Native FFmpeg-backed local decoder through OpenCV, without a raw-video pipe."""
import asyncio
import threading
import cv2
import numpy as np

class Decoder:
    def __init__(self,path,width,height,fps,position=0,loop=False):
        self.path,self.width,self.height,self.fps=path,width,height,fps
        self.position,self.loop=position,loop
        self.cap=None;self.frames=0;self.last=None;self.ended=False
        self.lock=threading.Lock();self.source_index=-1;self.last_target=-1
        self.source_fps=30;self.total=0

    async def start(self):
        await asyncio.to_thread(self.open)

    def open(self):
        with self.lock:
            self.cap=cv2.VideoCapture(str(self.path))
            if not self.cap.isOpened():
                raise RuntimeError('No se pudo abrir el video local')
            self.source_fps=self.cap.get(cv2.CAP_PROP_FPS) or 30
            self.total=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.start_index=int(self.position*self.source_fps)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES,self.start_index)
            self.source_index=self.start_index-1

    async def frame(self,paused=False,position=None):
        if (paused and self.last is not None) or self.ended:
            return self.last,False
        return await asyncio.to_thread(self.read,position)

    def read(self,position=None):
        with self.lock:
            if self.cap is None:
                return self.last,False
            wanted=int(position*self.source_fps) if position is not None else self.start_index+int(self.frames*self.source_fps/self.fps)
            if self.total and wanted>=self.total:
                if not self.loop:
                    self.ended=True;return self.last,False
                wanted%=self.total
            if wanted==self.last_target and self.last is not None:
                self.frames+=1;return self.last,False
            if wanted<self.source_index:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES,wanted)
                self.source_index=wanted-1
            while self.source_index<wanted-1:
                if not self.cap.grab():break
                self.source_index+=1
            ok,image=self.cap.read()
            if not ok:
                self.ended=True;return self.last,False
            self.source_index=wanted;self.last_target=wanted;self.frames+=1
            h,w=image.shape[:2];scale=min(self.width/w,self.height/h)
            scaled=cv2.resize(image,(max(1,round(w*scale)),max(1,round(h*scale))),interpolation=cv2.INTER_LINEAR)
            canvas=np.zeros((self.height,self.width,4),np.uint8);canvas[:,:,3]=255
            y=(self.height-scaled.shape[0])//2;x=(self.width-scaled.shape[1])//2
            canvas[y:y+scaled.shape[0],x:x+scaled.shape[1],:3]=scaled
            self.last=canvas.tobytes()
            return self.last,True

    async def close(self):
        def release():
            with self.lock:
                if self.cap:self.cap.release();self.cap=None
        await asyncio.to_thread(release)
