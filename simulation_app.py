# App to simulate a simple circuit with a resistor and a capacitor
# Author: Badr Alabsi 2024

import asyncio
import time
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
        ohmmeter.report(debug=True),
        ohmmeter2.report(debug=True)
    )

    # Print the readings for voltmeter 
    print(end="\n\n\n")
    print("Recorded voltmeter readings (🔋 voltage across R_L):")
    print("-" * 60)
    print(f"{'time':<9} |{'time_stamp':^30}| {'voltage':>12}")
    print("-" * 60)

    for reading in voltmeter.reading_record:
        print(f"{reading['time_step']/1000:<4.1f} sec {reading['time_stamp']:^30}   {reading['voltage']:>12.3f} V")

    # print the readings for ammeter
    print(end="\n\n\n")
    print("Recorded ammeter readings (⚡ current through R_L):")
    print("-" * 60)
    print(f"{'time':<9} |{'time_stamp':^30}| {'current':>12}")
    print("-" * 60)
    for reading in ammeter.reading_record:
        print(f"{reading['time_step']/1000:<4.1f} sec   {reading['time_stamp']:^30} {reading['current']:>12.3f} uA")


    # Restart the simulation
    #await circuit.restart()

if __name__ == "__main__":
    # Start the simulation using asyncio.run()

    print("Starting the simulation:")
    print("Time step: 100 msec")
    print("Real-time readings of Ohmmeter 1 (🧄 — 1 sec) and Ohmmeter 2 (🥕 — 2 sec): ")
    print("-" * 70)
    print(f"Device    |   time   |        System time        |       Reading")
    print("-" * 70)
    time.sleep(1)
    asyncio.run(main())
    print("-" * 70)