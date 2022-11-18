#
#
#   Get temperature i2c AE-SHT3X
#   accuracy is so-so
#

import time
import smbus

i2c_addr = 0x45
temp_decimal = 0

"""
def main():
    i2c = smbus.SMBus(1)

    i2c.write_byte_data(i2c_addr,0x21,0x30)
    time.sleep(0.1)

    while 1:
        i2c.write_byte_data(i2c_addr,0xE0,0x00)
        data = i2c.read_i2c_block_data(i2c_addr,0x00,6)
        result = temp_change(data[0],data[1])
        print(result)
        time.sleep(1)
"""

def temp_change(msb,lsb):
    mlsb = ((msb<<8)|lsb)
    return (-45 + 175 * int(str(mlsb),10)/(pow(2,16)-1))

def get_temp_byte(i2c):
    
    temp_decimal = 0
    i2c.write_byte_data(i2c_addr,0x21,0x30)
    time.sleep(0.1)
    byte_data = i2c.read_i2c_block_data(i2c_addr,0x00,6)
    temp_decimal = temp_change(byte_data[0],byte_data[1])
    return temp_decimal
