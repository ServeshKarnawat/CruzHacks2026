#include <stdio.h>
#include <stdlib.h>
#include <math.h> 
#include <Board.h>
#include <ADC.h>
#include <I2C.h>

#define IMU_ALPHA 0.2f       
#define FLEX_ALPHA 0.1f      
#define MOTION_THRESHOLD 0.01f 

int main(void) {
    BOARD_Init();
    ADC_Init();
    I2C_Init();

    I2C_WriteReg(0x6B, 0x10, 0x40); 
    
    float sX = 0, sY = 0, sZ = 0, sFlex = 0;
    
    
    float prevX = 0, prevY = 0, prevZ = 0;//variables to track the PREVIOUS state to detect change

    while (1) {
        uint16_t raw_flex = ADC_Read(ADC_CHANNEL_0);
        sFlex = (FLEX_ALPHA * raw_flex) + (1.0f - FLEX_ALPHA) * sFlex;

        //read imu
        int16_t rx = I2C_ReadInt(0x6B, 0x28, 0);
        int16_t ry = I2C_ReadInt(0x6B, 0x2A, 0);
        int16_t rz = I2C_ReadInt(0x6B, 0x2C, 0);

        //covernt to gs
        float curX = rx * 0.000061f;
        float curY = ry * 0.000061f;
        float curZ = rz * 0.000061f;

        //smoothening
        sX = (IMU_ALPHA * curX) + (1.0f - IMU_ALPHA) * sX;
        sY = (IMU_ALPHA * curY) + (1.0f - IMU_ALPHA) * sY;
        sZ = (IMU_ALPHA * curZ) + (1.0f - IMU_ALPHA) * sZ;

        //calculate change since last loop
        float deltaX = sX - prevX;
        float deltaY = sY - prevY;
        float deltaZ = sZ - prevZ;
        
        //magnitude of movement
        float movement_intensity = sqrtf(deltaX*deltaX + deltaY*deltaY + deltaZ*deltaZ);

        //directional logic based on movement
        char* dir = "STILL";
        
        //only report direction if significant change
        if (movement_intensity > MOTION_THRESHOLD) {
            if (fabsf(deltaX) > fabsf(deltaY) && fabsf(deltaX) > fabsf(deltaZ)) {
                dir = (deltaX > 0) ? "RIGHT" : "LEFT";
            } else if (fabsf(deltaY) > fabsf(deltaX) && fabsf(deltaY) > fabsf(deltaZ)) {
                dir = (deltaY > 0) ? "FORWARD" : "BACK";
            } else {
                dir = (deltaZ > 0) ? "UP" : "DOWN";
            }
        }

        //update for next loop
        prevX = sX;
        prevY = sY;
        prevZ = sZ;

        //debug output
        printf("%.1f,%.3f,%.3f,%.3f,%.4f,%s\r\n", sFlex, sX, sY, sZ, movement_intensity, dir);

        for(volatile int i = 0; i < 150000; i++); 
    }
}