# Software-Project

## Introduction
The product is designed for measuring the temperature dependence of resistance in various sample materials.
Our software eliminates the need for manual input parameter adjustments on the measuring device.
Unlike conventional experimentation methods that necessitate manual adjustment of input parameters such as
current and voltage on the measuring device, our software eliminates this labor-intensive step while ensuring
precision in data collection. The resistance vs time mode plots the graph between resistance that varies 
with increasing time at a particular temperature. The resistance vs temperature mode plots the graph between resistance varying with
change in temperature.

## How to get this software on your device?

- First, clone this repository on your device, using this command.

  `git clone https://github.com/Aditi202004/Software-Project.git`

- Then, install the required python libraries using the following command.

  `pip install requirements.txt`

- Then, run the file titled 

  `newInterfaceAndBackend.py`

## Setting Up and Performing the Experiment
- First, check if the connections are proper or not.
  - **GPIB**: current source to CPU
  - **RS-232 (male-to-male)** cable between current source and nanovoltmeter
  - **Trigger link cable**: between current source and nanovoltmeter
  - **Telnet cable**: CTC to CPU
  - GPIB interface is set for current source
  - RS-232 interface is set for nanovoltmeter
  - Baudrate of nanovoltmeter and current source should be 19.2 K
  - Flow control on nanovoltmeter should be set to NONE 
- Select the type of experiment you want to perform.
  - Resistance vs Time
  - Resistance vs Temperature
  - Note: you can select both modes at the same time also. <br>
  ( The different modes of the experiment have been explained further )
- You may click the Info button to get information about all the three devices and to check if they are connected or not.
- After that, click the Sync Set button to set all the values.
  - Note: you may also click the Sync Get button to use values from the previous experiment.
- Then, click the Trigger button to begin the experiment.
- If you wish to stop the experiment while it is still running, you can click the Abort button.

## Other Details
- If you wish to receive an email on completion of the experiment, click the corresponding button in the CTC tab.
- Click the Settings button to fill in your email ID.
- An email will be sent by the system to you on this email ID after the experiment is completed.

## What are the different modes of the experiment?

- Resistance vs Time mode
  - Inputs for the CTC:
    - Title: the name of the file to be stored.
    - Input channel: the channel through which input is provided.
    - Output channel: the channel through which output will be recorded.
    - Low limit: low limit of power (in Watts).
    - High limit: high limit of power (in Watts).
    - Increase by: the value by which power is to be increased (in Watts).
    - Max limit: maximum power that CTC can supply to increase by any temperature (in Watts).
    - P: P-value.
    - I: I-value.
    - D: D-value.
    - Threshold: error allowed for achieving the final value of temperature at which reading is to be taken (in Kelvin).
    - Tolerance: error allowed for stabilizing to the final value of temperature at which reading is to be taken (in Kelvin).
  - Inputs for current source:
    - High pulse: value of high pulse (in Ampere).
    - Low pulse: value of low pulse (in Ampere).
    - Total time: total time for which resistance is to be plotted.
    - Pulse width: wavelength of a single pulse (in seconds).
    - Number of pulses per second: number of pulses that will pass through in one second.
  - Required temperatures: temperatures at which resistance is to be plotted.
- Resistance vs Temperature mode
  - Inputs for the CTC:
    - The input fields will be the same as resistance vs time mode, with the following extra input fields:
      - Start temp: the temperature from which you wish to begin to take readings from (in Kelvin).
      - Stop temp: the temperature at which you wish to stop the readings (in Kelvin).
      - Increase temp by: interval by which temperature is to be increased (in Kelvin).
      - Delay of CTC: delay after which CTC will start increasing the temperature (in seconds).
      - Complete cycle: if this button is clicked, the experiment will perform both heating and cooling cycle.
  - Inputs for the current source:
    - Start current: minimum value of current that will be passed.
    - Stop current: maximum value of current that will be passed.
    - Increase current by: value by which current will be increased from start to stop current.
    - Delay of current source: delay after which current source will start supplying current to the sample.
  - If both the modes are selected, give the inputs accordingly as stated above.
