# A Python prgram to simulate an electric circuit with a given configuration 
# in real-time using the asyncio module 
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

        for i in range(0, 10100, self.reading_interval):
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
                print(f"Voltmeter t: {formatted_time:>6}, V: {self.circuit.V_L:>3.3f} V")

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

        for i in range(0, 10100, self.reading_interval):
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
                print(f"Ammeter t: {formatted_time:>6}, I: {I:>3.3f} uA")

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
        assert self.R1 >= 0, "R1 is negative"
        assert self.R2 >= 0, "R2 is negative"

        #R_total = self.compute_total_R()

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
        self.reset()
        await self.start()
    
    def reset(self):
         # set R1 and R2 to initial values and reset devices
        self.R1 = self.init_R1
        self.R2 = self.init_R2
        self.current_time_step.value = 0


async def main():
    # Instantiate the Circuit class
    circuit = Circuit(init_R1=0, init_R2=100000)

    # attach voltmeter and ammeter to the circuit
    voltmeter = Voltmeter(circuit, reading_interval=100)
    ammeter = Ammeter(circuit, reading_interval=300)

    # start the simulation
    # run the task concurrently by setting up the event loop

    await asyncio.gather(
        circuit.start(),
        voltmeter.start(debug=True),
        ammeter.start(debug=True)
    )


    for reading in voltmeter.reading_record:
        print(f"time: {reading['time_step']:>6} {reading['time_stamp']:>30} V: {reading['voltage']:>8.3f} V")

    for reading in ammeter.readings:
        print(f"time: {reading['time_step']:>6} {reading['time_stamp']:<30} I: {reading['current']:>8.3f} uA")

    # for reading in circuit.ammeter.readings:
    #     print(f"t: {reading['time']:>6}, I: {reading['current']:>3.3f} uA")


    # Restart the simulation
    #await circuit.restart()

if __name__ == "__main__":
    # Start the simulation using asyncio.run()
    asyncio.run(main())