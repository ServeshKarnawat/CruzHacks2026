#include <stdio.h>
#include <stdlib.h>
#include <Board.h>
#include <ADC.h>

#define ALPHA 1 // Smoothing factor (lower = smoother but slower)

int main(void)
{
    BOARD_Init();
    ADC_Init();

    float filtered_adc = 0;

    while (1)
    {
        uint16_t raw_adc = ADC_Read(ADC_CHANNEL_0);
        filtered_adc = (ALPHA * raw_adc) + ((1.0 - ALPHA) * filtered_adc);
        printf("%d,%.2f\r\n", raw_adc, filtered_adc);
        for(volatile int i = 0; i < 200000; i++); 
    }
}