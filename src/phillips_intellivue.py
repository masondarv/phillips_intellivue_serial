import serial
import serial.tools.list_ports as port_list

import socket
import sys
import struct
import time 
import datetime

class PhillipsIntellivue:
    
    def __init__(self):
        pass
    
    def init_serial(self):
        port = '/dev/cu.usbserial-14440'
        baudrate = 115200
        self.serial_port = serial.Serial(port=port, baudrate=baudrate,
                                bytesize=8, timeout=1, stopbits=serial.STOPBITS_ONE)
        
        
    def create_association_request(self):
        # default association requestt
        b=bytearray(b'\x0d\xff\x01\x28\x05\x08\x13\x01\x00\x16\x01\x02\x80\x00\x14\x02\x00\x02\xc1\xff\x01\x16\x31\x80\xa0\x80\x80\x01\x01\x00\x00\xa2\x80\xa0\x03\x00\x00\x01\xa4\x80\x30\x80\x02\x01\x01\x06\x04\x52\x01\x00\x01\x30\x80\x06\x02\x51\x01\x00\x00\x00\x00\x30\x80\x02\x01\x02\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x01\x01\x30\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x02\x01\x00\x00\x00\x00\x00\x00\x61\x80\x30\x80\x02\x01\x01\xa0\x80\x60\x80\xa1\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x03\x01\x00\x00\xbe\x80\x28\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x01\x01\x02\x01\x02\x81\x82\x00\x80\x80\x00\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x64\x00\x01\x00\x28\x80\x00\x00\x00\x00\x00\x0f\xa0\x00\x00\x05\xb0\x00\x00\x05\xb0\xff\xff\xff\xff\x60\x00\x00\x00\x00\x01\x00\x0c\xf0\x01\x00\x08\x8e\x00\x00\x00\x00\x00\x00\x00\x01\x02\x00\x34\x00\x06\x00\x30\x00\x01\x00\x21\x00\x00\x00\x01\x00\x01\x00\x06\x00\x00\x00\xc9\x00\x01\x00\x09\x00\x00\x00\x3c\x00\x01\x00\x05\x00\x00\x00\x10\x00\x01\x00\x2a\x00\x00\x00\x01\x00\x01\x00\x36\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        return b
    
    def check_assoc_response(self, b):
        n=0
        if b[:1]==bytearray(b'\x0E'):
            n=1
        return n
        
    def check_mds_event_report(self, b):
        n = 0
        if b[:6]==bytearray(b'\xe1\x00\x00\x02\x00\x01'):
            n=1
            #get base time
            self.get_basetime_from_MDS_attr_lst(b[34:])
        return n

    def mds_create_event_result(self, b):
        #extract relative_time
        d_l=list(struct.unpack('!I',b[20:24]))
        #increase relative_time
        e_time=struct.pack('!I',d_l[0]+50)
        #Construct MDS_result bytearray:
        #Session_id
        mds_result=b[:4]
        #head
        mds_result=mds_result+bytearray(b'\x00\x02\x00\x14')
        mds_result=mds_result+bytearray(b'\x00\x01\x00\x01\x00\x0e')
        mds_result=mds_result+bytearray(b'\x00\x21\x00\x00\x00\x00')
        #insert new timestamp
        mds_result=mds_result+e_time
        #Flags
        mds_result=mds_result+bytearray(b'\x0d\x06\x00\x00')
        return mds_result
        
    def create_poll_data_request(self, sid, n, nr, p_count):
        spr=bytearray()
        #session_id
        spr=spr+sid
        #head
        spr=spr+bytearray(b'\x00\x01\x00\x20')
        spr=spr+bytearray(b'\x00\x01\x00\x07\x00\x1a')
        spr=spr+bytearray(b'\x00\x21\x00\x00\x00\x00\x00\x00')
        #singe poll (1) or extended poll (2)
        if nr==1:
            spr=spr+bytearray(b'\x00\x00\x0C\x16')
        else:
            spr=spr+bytearray(b'\x00\x00\xf1\x3b')
        #length
        spr=spr+bytearray(b'\x00\x0C')
        #poll data request
        #poll number>counter
        spr=spr+struct.pack('!H', p_count)
        spr=spr+bytearray(b'\x00\x01')
        #metrics (1) or demogrphics (2)
        if n==1:
            spr=spr+bytearray(b'\x00\x06')
        else:
            spr=spr+bytearray(b'\x00\x2A')
        spr=spr+bytearray(b'\x00\x00')
        #from packet sniffing >> empiric appendix 00 00 00 00
        spr=spr+bytearray(b'\x00\x00\x00\x00')
        return spr
    
    
    def write_array(self, b):
        
        self.serial_port.write(b)
        
    def read_array(self):
        
        eof = "0xC1"
        buf = self.serial_port.read_until(expected=eof)
        print(buf)
        print("")
        return buf
    
    
    def send_assoc_request(self):
        self.write_array(self.create_association_request())
        
    
        
        
    



