# Real-time Electric Circuit Simulation 🪫⚡🔋

This repository contains Python code to simulate an electric circuit in real-time using asyncio module. The code was developed and tested using PYthon 3.11.5

## How to run

To run the code, follow these steps:

1. Clone the repository: `git clone https://github.com/your-username/simulate-circuit.git`
2. Navigate to the project directory: `cd simulate-circuit`
3. Run the command 
```
>>> python simulation_app.py
```

## Output format 
Check out the file [output.txt](https://github.com/badrex/simulate-circuit/blob/main/output.txt)



## Issues
The current implementation has some issues:

- It seems like the readings go out of sync due to the time each computational operation takes.
- For example, the readings of the first Ohmmeter go way below the expected 30 k-Ohm due to the mismatch of the timestamps.
- A possible solution to these issues is to introduce a system "clock" that each component has to follow.
- Rolling average in Ohmmeter 2 helps but it is still not accurate enough. 
- Alternatively, the simulation could be implemented using modules that do not implement concurrent processes.
- Additionally, the readings of the ammeter are behind by an offset of 100 msec. 