# A Python prgram to simulate an electric circuit with a given configuration 
# in real-time using the asyncio module 
# Author: Badr Alabsi 2024
import asyncio
import time
from datetime import datetime


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

        self.current_time_step = 0

        # time step in msec, for now changing this will cause problems
        # TODO: solve this issue
        self.time_step_size = 100 

    def parallel_R(self):
        """Return the parallel resistance R of R1 and RL in Ohms"""
        try: 
            R = (self.R2 * self.RL) / (self.R2 + self.RL)
        except ZeroDivisionError:
            R = float('inf')

        return R

    def total_R(self):
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



class ObservableAttribute:
    """
    A class to represent an observable object whose value
    can be observed by other objects
    """
    def __init__(self, initial_value=None):
        self._value = initial_value
        self._observers = []

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value != self._value:
            self._value = new_value
            self.notify_observers()

    def register_observer(self, observer):
        # add an observer funciton to the list of observers
        self._observers.append(observer)

    def notify_observers(self):
        # notify all observers when the value changes
        for observer in self._observers:
            observer()



class Voltmeter:
    """
    A class to represent a voltmeter device to read voltage 
    """
    def __init__(self, circuit, reading_interval=100):
        self.circuit = circuit
        self.reading_interval = reading_interval
        self.reading_record = []
        self.current_reading = ObservableAttribute(None)

    async def start(self, debug=False):
        """ read voltage voltage cross RL in the circuit """ 

        for i in range(0, 10001, self.reading_interval):
            now = datetime.now() # get the current time
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S") + f".{now.microsecond // 1000:03d}"

            self.current_reading.value = self.circuit.V_L

            self.reading_record.append(
                {
                    "time_step": i,
                    "time_stamp": formatted_time,
                    "voltage": self.current_reading.value
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
        self.current_reading.value = None
    

class Ammeter:
    """
    A class to represent an ammeter device to read current
    """
    def __init__(self, circuit, reading_interval=300):
        self.circuit = circuit
        self.reading_interval = reading_interval
        self.reading_record = []
        self.current_reading = ObservableAttribute(None)

    async def start(self, debug=False):
        """ read current I in the circuit """

        for i in range(0, 10001, self.reading_interval):
            # compute current I in through RL in microamperes
            I = (self.circuit.V_L / self.circuit.RL) * 1e6

            self.current_reading.value = I

            now = datetime.now() # get the current time
            formatted_time = now.strftime("%Y-%m-%d %H:%M:%S") + f".{now.microsecond // 1000:03d}"

            self.reading_record.append(
                {
                    "time_step": i,
                    "time_stamp": formatted_time,
                    "current": self.current_reading.value
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
        self.reading_record = []
        self.current_reading.value = None


class Ohmmeter:
    """
    A class to represent an ohmmeter device to read resistance
    """
    def __init__(self, circuit, voltmeter, ammeter, reading_interval=1000):
        self.circuit = circuit
        self.reading_interval = reading_interval

        # attach voltmeter and ammeter to the device
        self.voltmeter = voltmeter
        self.ammeter = ammeter
        self.voltmeter.current_reading.register_observer(self.update_reading)
        self.ammeter.current_reading.register_observer(self.update_reading)
        self.current_reading = None

        # to avoid reporting when ammeter has not been updated
        # this was added to avoid this scenario
        self.start_reporting = False


    def update_reading(self):
        """ read resistance R in the circuit """

        # calculate resistance RL based on volmeter and ammeter readings
        V = self.voltmeter.current_reading.value
        I = self.ammeter.current_reading.value

        if V and I: 
            self.current_reading =  1e3 * (V / I) # in kOhm
            self.start_reporting = True
    
    async def report(self, debug=False):
        """ read resistance R in the circuit """

        for i in range(0, 10001, self.reading_interval):
            # calculate resistance RL based on volmeter and ammeter readings
            if self.start_reporting:

                # get time now
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S") + f".{now.microsecond // 1000:03d}"

                if debug:
                    print(f"🧄 Ohm 1. {i/1000:>5} sec {formatted_time:^32}  {self.current_reading:>7.3f} kOhm")
            
                await asyncio.sleep(self.reading_interval/1000)

    def reset(self):
        """ reset the readings """
        self.readings = []


# a class derived from Ohmmeter 
class Ohmmeter2(Ohmmeter):
    """
    A class to represent an ohmmeter device to read resistance
    """
    def __init__(self, circuit, voltmeter, ammeter, reading_interval=2000):
        super().__init__(circuit, voltmeter, ammeter, reading_interval)
        self.past_readings = []

    def update_reading(self):
        """ read resistance R in the circuit """

        # calculate resistance RL based on volmeter and ammeter readings
        V = self.voltmeter.current_reading.value
        I = self.ammeter.current_reading.value

        if V and I: 
            self.current_reading =  1e3 * (V / I) # in kOhm
            self.start_reporting = True

            self.past_readings.append((V, I))

    async def report(self, debug=False):
        """ read resistance R in the circuit """

        for i in range(0, 10001, self.reading_interval):
            # calculate resistance RL based on volmeter and ammeter readings
            if self.start_reporting:

                # get the last 10 readings for voltage
                N = len(self.past_readings[-10:])
                sum_V = sum([V for V, _ in self.past_readings[-10:]])
                average_V = sum_V / N

                # get the last 6 readings for current
                M = len(self.past_readings[-6:])
                sum_I = sum([I for _, I in self.past_readings[-6:]])
                average_I = sum_I / M

                rolling_R = 1e3 * (average_V / average_I) # in kOhm

                # get time now
                now = datetime.now()
                formatted_time = now.strftime("%Y-%m-%d %H:%M:%S") + f".{now.microsecond // 1000:03d}"

                if debug:
                    print(f"🥕 Ohm 2. {i/1000:>5} sec {formatted_time:^32}  {rolling_R:>7.3f} kOhm", end='\n\n')
            
                await asyncio.sleep(self.reading_interval/1000)

    def current_reading(self):
        """ return the last reading """
        return self.reading_record[-1]
    
    def reset(self):
        """ reset the readings """
        self.readings = []