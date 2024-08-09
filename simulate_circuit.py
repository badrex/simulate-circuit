# A Python prgram to simulate an electric circuit with a given input and output 
# in real-time using the asyncio module 
import asyncio


class Circuit:
    """
    A class to simulate an electric circuit with in real-time
    """
    def __init__(self, init_R1, init_R2, RL=30000, Vin=10):
        self.init_R1 = init_R1
        self.init_R2 = init_R2

        self.R1 = self.init_R1
        self.R2 = self.init_R2

        self.RL = RL
        self.Vin = Vin

        self.time_step_size = 100 # in msec

    def compute_total_R(self):
        """Return total resistance R of the circuit in Ohms"""
        try: 
            R_total = self.R1 + ((1/self.R2) + (1/self.RL))
        except ZeroDivisionError: # if R2 = 0
            R_total = float('inf')

        return R_total

    async def update_status(self, time_step):
        """ update circuit parameters given current time step in msec"""
        self.R1 = self.init_R1 + 10*time_step
        self.R2 = self.init_R2 - 10*time_step

        R_total = self.compute_total_R()

        # Print current status
        ohm = "\u03A9"
        print(
            f"t: {time_step:>6} msec "
            f"R1: {self.R1/1000:>6.2f} k{ohm} "
            f"R2: {self.R2/1000:>6.2f} k{ohm} "
            f"Total R: {R_total/1000:>6.2f} k{ohm}"
        )

        await asyncio.sleep(self.time_step_size/1000)


    async def start(self):
        """
        start the simulation for 10 seconds with 100 msec timesteps
        """
        
        # loop through the simulation time for steps of 1 msec
        for t_step in range(0, 10100, self.time_step_size):

            await self.update_status(t_step)

    def restart(self):
        """
        Restart the simulation
        """
        self.R1 = self.init_R1
        self.R2 = self.init_R2
        self.start()

  

if __name__ == "__main__":
    # instantiate the Circuit class
    circuit = Circuit(0, 100000, RL=30000, Vin=10)

    # start the simulation
    asyncio.run(circuit.start())