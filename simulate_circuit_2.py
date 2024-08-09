# A Python prgram to simulate an electric circuit with a given input and output 
# in real-time using the asyncio module 
import asyncio

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
    def __init__(self, circuit):
        self.circuit = circuit
        self.circuit.current_time_step.register_observer(self.update_reading)
        self.time_step_interval = 100
        self.reading_record = []

    def update_reading(self):
        """ read voltage voltage on RL in the circuit """ 

        # check if time_step is a multiple of time_step_interval
        if self.circuit.current_time_step.value % self.time_step_interval == 0:
            self.reading_record.append(
                {
                    "time": self.circuit.current_time_step.value,
                    "voltage": self.circuit.V_L
                }
            ) 
        else:
            pass

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
    def __init__(self, circuit):
        self.circuit = circuit
        self.circuit.current_time_step.register_observer(self.update_reading)
        self.readin_interval = 300
        self.readings = []

    def update_reading(self):
        """ read current I in the circuit """

        # check if time_step is a multiple of readin_interval
        if self.circuit.current_time_step.value % self.readin_interval == 0:
            # compute current I in the circuit in microamperes
            I = self.circuit.V_L / self.circuit.RL * 1e6

            self.readings.append(
                {
                    "time": self.circuit.current_time_step.value,
                    "current": I
                }
            )
        else:
            pass

    def last_reading(self):
        """ return the last reading """
        return self.readings[-1]
    
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

        self.current_time_step = ObservableAttribute(0)
        self.time_step_size = 100 # in msec

        #self.voltmeter = Voltmeter(self)

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
        self.current_time_step.value = time_step
        self.R1 = self.init_R1 + 10*self.current_time_step.value
        self.R2 = self.init_R2 - 10*self.current_time_step.value

        R_total = self.compute_total_R()

        # compute voltage V_L across RL
        R = self.parallel_R()
        
        self.V_L = self.Vs * (R / (self.R1 + R)) 

        # if time_step is a multiplicanto of 100 
        # read voltage across RL
        # if time_step % 100 == 0:
        #     self.voltmeter.read(time_step, self)

        # if time_step % 300 == 0:
        #     self.ammeter.read(time_step, self)

        #print(self.voltmeter.last_reading())
    

        # Print current status - only for debugging
        # ohm = "\u03A9"
        # print(
        #     f"t: {time_step:>6} msec\t"
        #     f"R1: {self.R1/1000:>6.2f} k{ohm}\t"
        #     f"R2: {self.R2/1000:>6.2f} k{ohm}\t"
        #     f"Total R: {R_total/1000:>6.2f} k{ohm}"
        # )

        await asyncio.sleep(self.time_step_size/1000)


    async def start(self):
        """
        start the simulation for 10 seconds with 100 msec timesteps
        """
        
        # update circuit state every 100 msec
        for t_step in range(0, 10100, self.time_step_size):

            await self.update_state(t_step)


    async def restart(self):
        """ restart the simulation """

        # set R1 and R2 to initial values and reset devices
        self.R1 = self.init_R1
        self.R2 = self.init_R2
        self.voltmeter.reset()
        self.ammeter.reset()

        await self.start()


async def main():
    # Instantiate the Circuit class
    circuit = Circuit(0, 100000, RL=30000, Vs=10)

    # attach voltmeter and ammeter to the circuit
    voltmeter = Voltmeter(circuit)
    ammeter = Ammeter(circuit)

    # Start the simulation
    await circuit.start()

    for reading in voltmeter.reading_record:
        print(f"t: {reading['time']:>6}, V: {reading['voltage']:>3.3f} V")

    for reading in ammeter.readings:
        print(f"t: {reading['time']:>6}, I: {reading['current']:>3.3f} uA")

    # for reading in circuit.ammeter.readings:
    #     print(f"t: {reading['time']:>6}, I: {reading['current']:>3.3f} uA")


    # Restart the simulation
    #await circuit.restart()

if __name__ == "__main__":
    # Start the simulation using asyncio.run()
    asyncio.run(main())