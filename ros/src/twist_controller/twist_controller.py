from yaw_controller import YawController
from pid import PID
from lowpass import LowPassFilter

GAS_DENSITY = 2.858
ONE_MPH = 0.44704


class Controller(object):
    def __init__(self, vehicle_mass,fuel_capacity,brake_deadband,decel_limit,accel_limit,wheel_radius,wheel_base,steer_ratio,max_lat_accel,max_steer_angle, min_speed):
        # TODO: Implement
        self.yaw_controller = YawController(wheel_base, steer_ratio, min_speed, max_lat_accel, max_steer_angle)
        kp = 0.12
        ki = 0.006
        kd = 3.0
        self.pid = PID(kp, ki, kd)

    def control(self):
        # TODO: Change the arg, kwarg list to suit your needs
        # Return throttle, brake, steer
        # Calculate cte
        return 1., 0., 0.
