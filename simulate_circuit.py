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

        # compute voltage Vout across RL
        try: 
            R = (circuit.R2 * circuit.RL) / (circuit.R2 + circuit.RL)
        except ZeroDivisionError: # if R1 + R2 = 0
            R = float('inf')

        # calculate total current in the circuit
        I_L = circuit.Vs / (circuit.R1 + R)
        
        V_L = I_L * R

        self.readings.append(
            {
                "time": time_step,
                "R1": circuit.R1,
                "R2": circuit.R2,
                "R": R,
                "voltage": V_L
            }
        ) 

    def last_reading(self):
    
        """ return the last reading """
        return self.readings[-1]


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

        self.time_step_size = 100 # in msec

        # instantiate a voltmeter
        self.voltmeter = Voltmeter()


    def compute_total_R(self):
        """Return total resistance R of the circuit in Ohms"""
        try: 
            R_total = self.R1 + (self.R2 * self.RL) / (self.R2 + self.RL)
        except ZeroDivisionError: # if R1 + R2 = 0
            R_total = float('inf')

        return R_total


    async def update_state(self, time_step):
        """ update circuit parameters given current time step in msec"""
        self.R1 = self.init_R1 + 10*time_step
        self.R2 = self.init_R2 - 10*time_step

        R_total = self.compute_total_R()

        # read voltage across RL
        self.voltmeter.read(time_step, self)

        print(self.voltmeter.last_reading())
    

        # Print current status - only for debugging
        # ohm = "\u03A9"
        # print(
        #     f"t: {time_step:>6} msec "
        #     f"R1: {self.R1/1000:>6.2f} k{ohm} "
        #     f"R2: {self.R2/1000:>6.2f} k{ohm} "
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

        # set R1 and R2 to initial values 
        self.R1 = self.init_R1
        self.R2 = self.init_R2

        await self.start()


async def main():
    # Instantiate the Circuit class
    circuit = Circuit(0, 100000, RL=30000, Vs=10)

    # Start the simulation
    await circuit.start()

    #print(circuit.voltmeter.readings)


    # Restart the simulation
    #await circuit.restart()

if __name__ == "__main__":
    # Start the simulation using asyncio.run()
    asyncio.run(main())