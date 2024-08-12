# App to simulate a simple circuit with a resistor and a capacitor
# Author: Badr Alabsi 2024

import asyncio
from components import Circuit, Voltmeter, Ammeter, Ohmmeter, Ohmmeter2

async def main():
    # Instantiate the Circuit class
    circuit = Circuit(init_R1=0, init_R2=100000)

    # attach voltmeter and ammeter to the circuit
    voltmeter = Voltmeter(circuit, reading_interval=100)
    ammeter = Ammeter(circuit, reading_interval=300)
    ohmmeter = Ohmmeter(circuit, voltmeter, ammeter, reading_interval=1000)
    ohmmeter2 = Ohmmeter2(circuit, voltmeter, ammeter, reading_interval=2000)

    # start the simulation
    # run the task concurrently by setting up the event loop

    await asyncio.gather(
        circuit.start(),
        voltmeter.start(debug=False),
        ammeter.start(debug=False),
        ohmmeter.report(debug=False),
        ohmmeter2.report(debug=True)
    )


    # for reading in voltmeter.reading_record:
    #     print(f"time: {reading['time_step']:>6} {reading['time_stamp']:^30} V: {reading['voltage']:>8.3f} V")

    # for reading in ammeter.reading_record:
    #     print(f"time: {reading['time_step']:>6} {reading['time_stamp']:^30} I: {reading['current']:>8.3f} uA")


    # Restart the simulation
    #await circuit.restart()

if __name__ == "__main__":
    # Start the simulation using asyncio.run()
    asyncio.run(main())