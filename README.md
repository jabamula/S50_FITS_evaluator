# S50_FITS_evaluator
Evaluates the center positions of Seestar S50 FITS files that are debayered and plate solved good quality files. Use only either Seestar approved or based on your own checking.

The program will ask the user to choose the files. Remember to give them in the chronological order from the oldest file on.
It will get the Right Ascension and Declination coordinates from the center of the First File and following graphs:

Figure 1: **RA/DEC wandering scatter plot** in the FOV of the Seestar as well as **X/Y wandering plot** from the center of the first image zoomed to show the wandering area.
![Deneb Wandering Figure_1](https://github.com/user-attachments/assets/c17988a9-8114-4d5f-ab75-a20988dd4532)

Figure 2: **Image center point wanderings** from the start of the observation. Scatter plot for each wandered distance and line plot for the distance to the center of the first file.
![Deneb Wandering Figure_2](https://github.com/user-attachments/assets/e2da9aa4-dc64-465b-960b-84ef78e4f7f2)

The app generates the **object_coordinates.csv** file to the root of the application.
<img width="1174" alt="object_coordinates csv" src="https://github.com/user-attachments/assets/428c8fe7-528e-409f-b9f1-e5a7a3a71d03">
