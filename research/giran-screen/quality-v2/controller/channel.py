"""The existing x86 L2 relay ABI. Read only our camera frames; publish program output."""
import ctypes as C
import struct
from pathlib import Path

WIDTH, HEIGHT, HEADER = 1280, 960, 24
SIZE = HEADER + WIDTH * HEIGHT * 4
MAGIC = 0x3256544E
CAMERA = 'Local\\NexusGiranTV_v1'
PROGRAM = 'Local\\NexusGiranTV_Program_v2'
LEGACY_PROGRAM = 'Local\\NexusGiranTV_Program_v1'
k = C.WinDLL('kernel32', use_last_error=True)
k.OpenFileMappingW.argtypes = [C.c_uint, C.c_int, C.c_wchar_p]
k.OpenFileMappingW.restype = C.c_void_p
k.CreateFileMappingW.argtypes = [C.c_void_p, C.c_void_p, C.c_uint, C.c_uint, C.c_uint, C.c_wchar_p]
k.CreateFileMappingW.restype = C.c_void_p
k.MapViewOfFile.argtypes = [C.c_void_p, C.c_uint, C.c_uint, C.c_uint, C.c_size_t]
k.MapViewOfFile.restype = C.c_void_p
k.UnmapViewOfFile.argtypes = [C.c_void_p]
k.CloseHandle.argtypes = [C.c_void_p]
k.GetTickCount64.restype = C.c_ulonglong
k.CreateMutexW.argtypes = [C.c_void_p, C.c_int, C.c_wchar_p]
k.CreateMutexW.restype = C.c_void_p
publisher = C.WinDLL(str(Path(__file__).with_name('publisher_hd.dll')))
publisher.PublishFrame.argtypes = [C.c_void_p, C.c_void_p, C.c_uint]
publisher.PublishFrame.restype = C.c_int
publisher.PublishFrameHD.argtypes = [C.c_void_p, C.c_void_p, C.c_uint]
publisher.PublishFrameHD.restype = C.c_int

class Channel:
    def __init__(self, name, write=False, legacy=False):
        self.write = write
        self.sequence = -1
        self.width, self.height, self.magic = (512, 384, 0x3156544E) if legacy else (WIDTH, HEIGHT, MAGIC)
        self.size = HEADER + self.width * self.height * 4
        self.handle = (k.CreateFileMappingW(C.c_void_p(-1), None, 4, 0, self.size, name)
                       if write else k.OpenFileMappingW(4, False, name))
        self.ptr = k.MapViewOfFile(self.handle, 0xF001F if write else 4, 0, 0, self.size) if self.handle else None
        if self.handle and not self.ptr:
            k.CloseHandle(self.handle)
            self.handle = None

    def publish(self, pixels):
        if not self.ptr or not self.write or len(pixels) != self.width * self.height * 4:
            raise ValueError('Invalid program frame')
        fn = publisher.PublishFrame if self.width == 512 else publisher.PublishFrameHD
        if not fn(self.ptr, pixels, len(pixels)):
            raise RuntimeError('No se pudo publicar el frame.')

    def read(self):
        if not self.ptr:
            return None, None
        for _ in range(3):
            seq, magic, w, h, tick = struct.unpack('<IIIIQ', C.string_at(self.ptr, HEADER))
            if seq & 1 or magic != self.magic or (w, h) != (self.width, self.height):
                continue
            pixels = C.string_at(self.ptr + HEADER, self.width * self.height * 4)
            if seq == C.c_long.from_address(self.ptr).value:
                self.sequence = seq
                return pixels, max(0, k.GetTickCount64() - tick)
        return None, None

    def close(self):
        if self.ptr:
            k.UnmapViewOfFile(self.ptr)
            self.ptr = None
        if self.handle:
            k.CloseHandle(self.handle)
            self.handle = None
