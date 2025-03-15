from machine import Pin, I2C, SPI
import utime, math, random
from max7219 import Matrix8x8
i2c = I2C(0, scl=Pin(9), sda=Pin(8), freq=400000)
spi = SPI(0, baudrate=10000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))
display = Matrix8x8(spi, Pin(10), 4) 
MPU6050_ADDR = 0x68
i2c.writeto_mem(MPU6050_ADDR, 0x6B, b'\x00')
def read_raw_data(addr):
    data = i2c.readfrom_mem(MPU6050_ADDR, addr, 2)
    value = (data[0] << 8) | data[1]
    if value > 32767:
        value -= 65536
    return value
MAX_SAND = 100
sand_particles = [(random.randint(0, 31), random.randint(0, 7)) for _ in range(MAX_SAND)] 
while True:
    acc_x = read_raw_data(0x3B)
    acc_y = read_raw_data(0x3D)
    acc_z = read_raw_data(0x3F)
    acc_x = acc_x / 16384.0
    acc_y = acc_y / 16384.0
    acc_z = acc_z / 16384.0
    x_angle = math.atan2(acc_y, acc_z) * (180 / math.pi) 
    y_angle = math.atan2(acc_x, acc_z) * (180 / math.pi)  
    print(f"X Angle: {x_angle:.2f}°, Y Angle: {y_angle:.2f}°") 
    gravity_down = not (y_angle > 90 or y_angle < -90) 
    occupied = set(sand_particles)
    new_positions = []
    sand_particles.sort(key=lambda p: p[1], reverse=gravity_down)  
    for x, y in sand_particles:
        new_x, new_y = x, y
        if gravity_down:
            if y < 7 and (x, y + 1) not in occupied:  
                new_y = y + 1
            else:
                if x_angle > 10 and x < 31 and (x + 1, y) not in occupied:
                    new_x = x + 1
                elif x_angle < -10 and x > 0 and (x - 1, y) not in occupied:
                    new_x = x - 1
        else:
            if y > 0 and (x, y - 1) not in occupied: 
                new_y = y - 1
            else: 
                if x_angle > 10 and x < 31 and (x + 1, y) not in occupied:
                    new_x = x - 1
                elif x_angle < -10 and x > 0 and (x - 1, y) not in occupied:
                    new_x = x + 1
        new_positions.append((new_x, new_y))
    sand_particles = list(set(new_positions)) 
    while len(sand_particles) < MAX_SAND:
        new_sand = (random.randint(0, 31), 0)
        if new_sand not in sand_particles:
            sand_particles.append(new_sand)

    # Display sand
    display.fill(0)
    for x, y in sand_particles:
        display.pixel(x, y, 1)
    display.show()

    utime.sleep(0.1)

