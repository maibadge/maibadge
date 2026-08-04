"""Single-owner PWM buzzer output."""

import pwmio

import config


class Buzzer:
    def __init__(self):
        self._pwm = pwmio.PWMOut(
            config.BUZZER_PIN,
            frequency=440,
            duty_cycle=0,
            variable_frequency=True,
        )

    def tone(self, frequency):
        if frequency and frequency > 0:
            self._pwm.frequency = max(20, int(frequency))
            self._pwm.duty_cycle = config.BUZZER_DUTY
        else:
            self.off()

    def off(self):
        self._pwm.duty_cycle = 0

    def deinit(self):
        self.off()
        self._pwm.deinit()
