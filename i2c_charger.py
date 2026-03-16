from machine import I2C, Pin
# Pylint users ignore import warning

R1 = 100000
R2 = 10000
VBAT_MULT = R2 / (R1 + R2)

R3 = 1
R4 = 1
IBAT_MULT = 1

SCL_PIN = 7
SDA_PIN = 6

DEVICE_ADDR = 0x6B

i2c = I2C(0, scl=Pin(SCL_PIN), sda=SDA_PIN)

def read_16bit_reg(address):
    data = i2c.readfrom_mem(DEVICE_ADDR, address, 2)
    raw_val = data[0] | (data[1] << 8)
    return raw_val

def set_charge_voltage(tmv):
    OFFSET_MV = 1504
    STEP_MV = 2

    if tmv < 1504:
        tmv = 1504
    elif tmv > 1566:
        tmv = 1566

    reg_value = (tmv - OFFSET_MV) // STEP_MV
    formatted = reg_value & 0x1F

    i2c.writeto_mem(DEVICE_ADDR, 0x0, bytes([formatted]))

def set_charge_amperage(tma):
    STEP_MA = 50

    if tma < 400:
        tma = 400
    elif tma > 20000:
        tma = 20000
    
    reg_value = tma // STEP_MA
    final_value = reg_value << 2

    lowbyte = final_value & 0xFF
    highbyte = (final_value >> 8) & 0xFF

    i2c.writeto_mem(DEVICE_ADDR, 0x2, bytes([lowbyte, highbyte]))

def get_vbat_adc():
    vbat_raw = read_16bit_reg(0x33)
    v_fb = vbat_raw / 1000.0
    actual_voltage = v_fb * VBAT_MULT
    return actual_voltage

def get_ibat_adc():
    ibat_raw = read_16bit_reg(0x2F)
    if ibat_raw & 0x8000:
        ibat_signed = ibat_raw - 0x10000
    else:
        ibat_signed = ibat_raw
    actual_amperage = (ibat_signed * 2) / 1000.0
    return actual_amperage