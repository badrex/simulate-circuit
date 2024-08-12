# A Python prgram to simulate an electric circuit with a given input and output 
# in real-time using the asyncio module 
import asyncio


class Voltmeter:
    """
    A class to represent a voltmeter device to read voltage 
    """
    def __init__(self):
        self.readings = []

    def read(self, time_step, circuit):
        """ read voltage voltage on RL in the circuit """ 

        self.readings.append(
            {
                "time": time_step,
                "voltage": circuit.V_L
            }
        ) 

    def last_reading(self):
    
        """ return the last reading """
        return self.readings[-1]
    
    def reset(self):
        """ reset the readings """
        self.readings = []
    

class Ammeter:
    """
    A class to represent an ammeter device to read current
    """
    def __init__(self):
        self.readings = []

    def read(self, time_step, circuit):
        """ read current I in the circuit """

        # compute current I in the circuit in microamperes
        I = circuit.V_L / circuit.RL * 1e6

        self.readings.append(
            {
                "time": time_step,
                "current": I
            }
        )

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

        self.time_step_size = 100 # in msec

        # instantiate a voltmeter and an ammeter
        self.voltmeter = Voltmeter()
        self.ammeter = Ammeter()

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
        self.R1 = self.init_R1 + 10*time_step
        self.R2 = self.init_R2 - 10*time_step

        R_total = self.compute_total_R()

        # compute voltage V_L across RL
        R = self.parallel_R()
        
        self.V_L = self.Vs * (R / (self.R1 + R)) 

        # if time_step is a multiplicanto of 100 
        # read voltage across RL
        if time_step % 100 == 0:
            self.voltmeter.read(time_step, self)

        if time_step % 300 == 0:
            self.ammeter.read(time_step, self)

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

    # Start the simulation
    await circuit.start()

    for reading in circuit.voltmeter.readings:
        print(f"t: {reading['time']:>6}, V: {reading['voltage']:>3.3f} V")

    for reading in circuit.ammeter.readings:
        print(f"t: {reading['time']:>6}, I: {reading['current']:>3.3f} uA")


    # Restart the simulation
    #await circuit.restart()

if __name__ == "__main__":
    # Start the simulation using asyncio.run()
    asyncio.run(main())