# A Python prgram to simulate an electric circuit with a given configuration 
# in real-time using the asyncio module 
# Author: Badr Alabsi 2024
import asyncio
import time
from datetime import datetime



class Voltmeter:
    """
    A class to represent a voltmeter device to read voltage 
    """
    def __init__(self, circuit, reading_interval=100):
        self.circuit = circuit
        self.reading_interval = reading_interval
        self.reading_record = []

    async def start(self, debug=False):
        """ read voltage voltage cross RL in the circuit """ 

        for i in range(0, 10001, self.reading_interval):
            now = datetime.now() # get the current time
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S") + f".{now.microsecond // 1000:03d}"

            self.reading_record.append(
                {
                    "time_step": i,
                    "time_stamp": formatted_time,
                    "voltage": self.circuit.V_L
                }
            )
            # for debugging
            if debug:
                print(f"Vol. t: {formatted_time:^30} V: {self.circuit.V_L:>8.3f} V")

            await asyncio.sleep(self.reading_interval/1000)

    def last_reading(self):
    
        """ return the last reading """
        return self.reading_record[-1]
    
    def reset(self):
        """ reset the readings """
        self.reading_record = []
    

class Ammeter:
    """
    A class to represent an ammeter device to read current
    """
    def __init__(self, circuit, reading_interval=300):
        self.circuit = circuit
        self.reading_interval = reading_interval
        self.reading_record = []

    async def start(self, debug=False):
        """ read current I in the circuit """

        for i in range(0, 10001, self.reading_interval):
            # compute current I in through RL in microamperes
            I = (self.circuit.V_L / self.circuit.RL) * 1e6

            now = datetime.now() # get the current time
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S") + f".{now.microsecond // 1000:03d}"

            self.reading_record.append(
                {
                    "time_step": i,
                    "time_stamp": formatted_time,
                    "current": I
                }
            )
            # for debugging
            if debug:
                print(f"Amm. t: {formatted_time:^30} I: {I:>8.3f} uA")

            await asyncio.sleep(self.reading_interval/1000)

    def last_reading(self):
        """ return the last reading """
        return self.reading_record[-1]
    
    def reset(self):
        """ reset the readings """
        self.readings = []


class Circuit:
    """
    A class to simulate an electric circuit with in real-time
    """
    def __init__(self, init_R1, init_R2, RL=30000, Vs=10):
        self.init_R1 = init_R1
        self.init_R2 = init_R2

        self.R1 = self.init_R1
        self.R2 = self.init_R2

        self.RL = RL
        self.Vs = Vs
        self.V_L = 0

        self.time_step_size = 100 # in msec
        self.current_time_step = 0


    def parallel_R(self):
        """Return the parallel resistance R of R1 and RL in Ohms"""
        try: 
            R = (self.R2 * self.RL) / (self.R2 + self.RL)
        except ZeroDivisionError:
            R = float('inf')

        return R

    def compute_total_R(self):
        """Return total resistance R of the circuit in Ohms"""
        return self.R1 + self.parallel_R()


    async def update_state(self, time_step):
        """ update circuit parameters given current time step in msec"""
        self.current_time_step = time_step
        self.R1 = self.init_R1 + 10*self.current_time_step
        self.R2 = self.init_R2 - 10*self.current_time_step

        # make sure R1 and R2 are not negative by asserting
        assert self.R1 >= 0, f"R1 is negative at {self.current_time_step}"
        assert self.R2 >= 0, f"R2 is negative at {self.current_time_step}"

        #R_total = self.compute_total_R()

        # compute voltage V_L across RL
        R = self.parallel_R()
        
        self.V_L = self.Vs * (R / (self.R1 + R)) 

        await asyncio.sleep(self.time_step_size/1000)


    async def start(self):
        """
        start the simulation for 10 seconds with 100 msec timesteps
        """
        
        # update circuit state every 100 msec
        for t_step in range(0, 10001, self.time_step_size):

            await self.update_state(t_step)


    async def restart(self):
        """ restart the simulation """
        self.reset()
        await self.start()
    
    def reset(self):
         # set R1 and R2 to initial values and reset devices
        self.R1 = self.init_R1
        self.R2 = self.init_R2
        self.current_time_step.value = 0