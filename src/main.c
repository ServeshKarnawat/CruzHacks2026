#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h> 
#include <Board.h>
#include <ADC.h>
#include <I2C.h>
#include <pwm.h>

#define IMU_ALPHA 0.2f       
#define FLEX_ALPHA 0.1f      
#define MOTION_THRESHOLD 0.01f 


typedef enum { STATE_STEADY, STATE_GOING_UP } RepState;

int main(void) {
    
    BOARD_Init();
    ADC_Init();
    I2C_Init();
    
    PWM_Init();
    PWM_AddPin(PWM_0);           
    PWM_SetDutyCycle(PWM_0, 0);  


    I2C_WriteReg(0x6B, 0x10, 0x40); 
    

    float sX = 0, sY = 0, sZ = 0, sFlex = 0;
    float prevX = 0, prevY = 0, prevZ = 0;
    int freq;

    
    RepState current_state = STATE_STEADY;
    bool peak_reached = false;
    int rep_count = 0;

    while (1) {
        //read flex sensor
        uint16_t raw_flex = ADC_Read(ADC_CHANNEL_0);
        sFlex = (FLEX_ALPHA * raw_flex) + (1.0f - FLEX_ALPHA) * sFlex;

        //rep tracking
        if (current_state == STATE_STEADY) {
            //trigger start of rep when flex exceeds steady state
            if (sFlex > 50) { 
                current_state = STATE_GOING_UP;
                peak_reached = false; 
            }
        } 
        else if (current_state == STATE_GOING_UP) {
            //register if peak reached
            if (sFlex > 130) {
                peak_reached = true;
            }

            //rep ends user returns to steady
            if (sFlex < 40) {
                if (peak_reached) {
                    rep_count++;
                    freq = 800;
                    PWM_SetFrequency(freq);      // High beep for Success
                    PWM_SetDutyCycle(PWM_0, 50);
                } else {
                    freq = 300;
                    PWM_SetFrequency(freq);       // Low beep for Fail
                    PWM_SetDutyCycle(PWM_0, 50);
                }
                
                //blockling delays
                for(volatile int i = 0; i < 800000; i++); 
                
                PWM_SetDutyCycle(PWM_0, 0);  
                current_state = STATE_STEADY;    
            }
        }

        //imu data
        int16_t rx = I2C_ReadInt(0x6B, 0x28, 0);
        int16_t ry = I2C_ReadInt(0x6B, 0x2A, 0);
        int16_t rz = I2C_ReadInt(0x6B, 0x2C, 0);

        float curX = rx * 0.000061f;
        float curY = ry * 0.000061f;
        float curZ = rz * 0.000061f;

        //low pass f
        sX = (IMU_ALPHA * curX) + (1.0f - IMU_ALPHA) * sX;
        sY = (IMU_ALPHA * curY) + (1.0f - IMU_ALPHA) * sY;
        sZ = (IMU_ALPHA * curZ) + (1.0f - IMU_ALPHA) * sZ;

        float stability = fabsf(sX*sX) + fabsf(sY*sY) + fabsf(sZ*sZ); // Total sum of X, Y, and Z

        //high pass f
        float deltaX = sX - prevX;
        float deltaY = sY - prevY;
        float deltaZ = sZ - prevZ;
        float movement_intensity = sqrtf(deltaX*deltaX + deltaY*deltaY + deltaZ*deltaZ);

        //direction
        char* dir = "STILL";
        if (movement_intensity > MOTION_THRESHOLD) {
            if (fabsf(deltaX) > fabsf(deltaY) && fabsf(deltaX) > fabsf(deltaZ)) {
                dir = (deltaX > 0) ? "RIGHT" : "LEFT";
            } else if (fabsf(deltaY) > fabsf(deltaX) && fabsf(deltaY) > fabsf(deltaZ)) {
                dir = (deltaY > 0) ? "FORWARD" : "BACK";
            } else {
                dir = (deltaZ > 0) ? "UP" : "DOWN";
            }
        }

        //update
        prevX = sX; prevY = sY; prevZ = sZ;

        //debug csv
        printf("%.1f,%.3f,%.3f,%.3f,%.3f,%.4f,%s,%d\r\n", 
       sFlex, sX, sY, sZ, stability, movement_intensity, dir, rep_count);

        for(volatile int i = 0; i < 1500; i++); 
    }
}