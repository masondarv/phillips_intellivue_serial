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
    def crc_ccit(self, input_msg):
        
        '''
        CRC-16 (CCITT) implemented with a precomputed lookup table
        See https://www.fdi.ucm.es/profesor/mendias/TFE/recursos/OTROS/IrLAP11.PDF
        '''
        
        fcstab = [0x0000, 0x1189, 0x2312, 0x329b, 0x4624, 0x57ad, 0x6536, 0x74bf,
                  0x8c48, 0x9dc1, 0xaf5a, 0xbed3, 0xca6c, 0xdbe5, 0xe97e, 0xf8f7,
                  0x1081, 0x0108, 0x3393, 0x221a, 0x56a5, 0x472c, 0x75b7, 0x643e,
                  0x9cc9, 0x8d40, 0xbfdb, 0xae52, 0xdaed, 0xcb64, 0xf9ff, 0xe876,
                  0x2102, 0x308b, 0x0210, 0x1399, 0x6726, 0x76af, 0x4434, 0x55bd,
                  0xad4a, 0xbcc3, 0x8e58, 0x9fd1, 0xeb6e, 0xfae7, 0xc87c, 0xd9f5,
                  0x3183, 0x200a, 0x1291, 0x0318, 0x77a7, 0x662e, 0x54b5, 0x453c,
                  0xbdcb, 0xac42, 0x9ed9, 0x8f50, 0xfbef, 0xea66, 0xd8fd, 0xc974,
                  0x4204, 0x538d, 0x6116, 0x709f, 0x0420, 0x15a9, 0x2732, 0x36bb,
                  0xce4c, 0xdfc5, 0xed5e, 0xfcd7, 0x8868, 0x99e1, 0xab7a, 0xbaf3,
                  0x5285, 0x430c, 0x7197, 0x601e, 0x14a1, 0x0528, 0x37b3, 0x263a,
                  0xdecd, 0xcf44, 0xfddf, 0xec56, 0x98e9, 0x8960, 0xbbfb, 0xaa72,
                  0x6306, 0x728f, 0x4014, 0x519d, 0x2522, 0x34ab, 0x0630, 0x17b9,
                  0xef4e, 0xfec7, 0xcc5c, 0xddd5, 0xa96a, 0xb8e3, 0x8a78, 0x9bf1,
                  0x7387, 0x620e, 0x5095, 0x411c, 0x35a3, 0x242a, 0x16b1, 0x0738,
                  0xffcf, 0xee46, 0xdcdd, 0xcd54, 0xb9eb, 0xa862, 0x9af9, 0x8b70,
                  0x8408, 0x9581, 0xa71a, 0xb693, 0xc22c, 0xd3a5, 0xe13e, 0xf0b7,
                  0x0840, 0x19c9, 0x2b52, 0x3adb, 0x4e64, 0x5fed, 0x6d76, 0x7cff,
                  0x9489, 0x8500, 0xb79b, 0xa612, 0xd2ad, 0xc324, 0xf1bf, 0xe036,
                  0x18c1, 0x0948, 0x3bd3, 0x2a5a, 0x5ee5, 0x4f6c, 0x7df7, 0x6c7e,
                  0xa50a, 0xb483, 0x8618, 0x9791, 0xe32e, 0xf2a7, 0xc03c, 0xd1b5,
                  0x2942, 0x38cb, 0x0a50, 0x1bd9, 0x6f66, 0x7eef, 0x4c74, 0x5dfd,
                  0xb58b, 0xa402, 0x9699, 0x8710, 0xf3af, 0xe226, 0xd0bd, 0xc134,
                  0x39c3, 0x284a, 0x1ad1, 0x0b58, 0x7fe7, 0x6e6e, 0x5cf5, 0x4d7c,
                  0xc60c, 0xd785, 0xe51e, 0xf497, 0x8028, 0x91a1, 0xa33a, 0xb2b3,
                  0x4a44, 0x5bcd, 0x6956, 0x78df, 0x0c60, 0x1de9, 0x2f72, 0x3efb,
                  0xd68d, 0xc704, 0xf59f, 0xe416, 0x90a9, 0x8120, 0xb3bb, 0xa232,
                  0x5ac5, 0x4b4c, 0x79d7, 0x685e, 0x1ce1, 0x0d68, 0x3ff3, 0x2e7a,
                  0xe70e, 0xf687, 0xc41c, 0xd595, 0xa12a, 0xb0a3, 0x8238, 0x93b1,
                  0x6b46, 0x7acf, 0x4854, 0x59dd, 0x2d62, 0x3ceb, 0x0e70, 0x1ff9,
                  0xf78f, 0xe606, 0xd49d, 0xc514, 0xb1ab, 0xa022, 0x92b9, 0x8330,
                  0x7bc7, 0x6a4e, 0x58d5, 0x495c, 0x3de3, 0x2c6a, 0x1ef1, 0x0f78]
        
        crc = 0xFFFF
        for byte in input_msg:
            crc = (crc << 8) ^ fcstab[(crc >> 8) ^ byte]
            crc &= 0xFFFF      
        return crc

        
    def create_packet(self, user_data):
        
        '''
        Create transport layer packet
        
        See https://file.notion.so/f/f/0395e570-5025-415d-8ea9-1b1b9367ab4a/332a53b2-401c-4f1c-a7ff-ccd900aec860/fdocuments.us_data-export-interface-programming-guide.pdf?id=3bc26b68-551e-4c40-bc6c-9440cde6e552&table=block&spaceId=0395e570-5025-415d-8ea9-1b1b9367ab4a&expirationTimestamp=1715623200000&signature=acbzPQ4q3i0TunOoI7IdaHyvRTdhSZQKKwwoTJVdrQI&downloadName=fdocuments.us_data-export-interface-programming-guide.pdf
        
        Page 30
        '''
        
        # start with Beginning of Frame byte
        packet = bytearray()
        bof = bytearray(b'\0xc0')
        # add bof to packet
        packet.extend(bof)
        
        # build transport header
        protocol_id = bytearray(b'\0x11')
        msg_type = bytearray(b'\0x01')
        
        length = len(user_data)
        lenb1 = (length & 0xFF00) >> 8
        lenb2 = length & 0x00FF
        print(f'Length: {length}')
        lenb1 =  hex(lenb1)
        lenb2 = hex(lenb2)
        lenb1 = bytearray(lenb1, 'utf-8')
        lenb2 = bytearray(lenb2, 'utf-8')
        print(f'lenb1: {lenb1}')
        print(f'lenb2: {lenb2}')
        length_array = bytearray()
        length_array.extend(lenb1)
        length_array.extend(lenb2)
        print(f'length_array: {length_array}')
        
        transport_hdr = bytearray()
        transport_hdr.extend(protocol_id)
        transport_hdr.extend(msg_type)
        transport_hdr.extend(length_array)
        packet.extend(transport_hdr)
        
        #append user data to packet
        packet.extend(user_data)
        
        
        # compute CRC using CRC-CCCIT algorithm
        crc_input = bytearray()
        crc_input.extend(transport_hdr)
        crc_input.extend(user_data)
        
        fcs = self.crc_ccit(crc_input)
        print(f"fcs: {fcs}")
        fcs_b1 = (fcs & 0xFF00) >> 8
        fcs_b2 = fcs & 0x00FF
        fcs_b1 = bytearray(hex(fcs_b1), 'utf-8')
        fcs_b2 = bytearray(hex(fcs_b2), 'utf-8')
        
        packet.extend(fcs_b1)
        packet.extend(fcs_b2)
        
        
        
        # append End of Frame to complete packet
        eof = bytearray(b'0xc1')
        
        packet.extend(eof)
        
        return packet
        

        
        
    def create_association_request(self):
        # default association request
        user_data =bytearray(b'\x0d\xff\x01\x28\x05\x08\x13\x01\x00\x16\x01\x02\x80\x00\x14\x02\x00\x02\xc1\xff\x01\x16\x31\x80\xa0\x80\x80\x01\x01\x00\x00\xa2\x80\xa0\x03\x00\x00\x01\xa4\x80\x30\x80\x02\x01\x01\x06\x04\x52\x01\x00\x01\x30\x80\x06\x02\x51\x01\x00\x00\x00\x00\x30\x80\x02\x01\x02\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x01\x01\x30\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x02\x01\x00\x00\x00\x00\x00\x00\x61\x80\x30\x80\x02\x01\x01\xa0\x80\x60\x80\xa1\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x03\x01\x00\x00\xbe\x80\x28\x80\x06\x0c\x2a\x86\x48\xce\x14\x02\x01\x00\x00\x00\x01\x01\x02\x01\x02\x81\x82\x00\x80\x80\x00\x00\x00\x40\x00\x00\x00\x00\x00\x00\x00\x80\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x00\x02\x00\x64\x00\x01\x00\x28\x80\x00\x00\x00\x00\x00\x0f\xa0\x00\x00\x05\xb0\x00\x00\x05\xb0\xff\xff\xff\xff\x60\x00\x00\x00\x00\x01\x00\x0c\xf0\x01\x00\x08\x8e\x00\x00\x00\x00\x00\x00\x00\x01\x02\x00\x34\x00\x06\x00\x30\x00\x01\x00\x21\x00\x00\x00\x01\x00\x01\x00\x06\x00\x00\x00\xc9\x00\x01\x00\x09\x00\x00\x00\x3c\x00\x01\x00\x05\x00\x00\x00\x10\x00\x01\x00\x2a\x00\x00\x00\x01\x00\x01\x00\x36\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

        print(f'User Data {user_data}')
        assoc_request = self.create_packet(user_data)
        
        print(f'Association Request Packet: {assoc_request}')
        
        
        return assoc_request
    
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
        
    
        
        
    



