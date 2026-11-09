# **Problem/Claim**
The tool addresses the challenge that comes when trying to do a comparison of Windows from an old model compared to a new model of that same building.
Mainly used in renovation projects.    

# **Source of the Problem**
The main problem occurred when looking through old LCA reports of renovation projects of the building 308 at DTU-Lyngby done through the course "Advanced buildingdesign". It was easy to make an script returning the total square meter of windows used. The main difficulty was to get it to show the newly implemented windows. This has been done by comparing an ifc file of the old building with an ifc file of the renovated version of said building. 
By running this script it shows the difference in window area between the two files and therefore solves this problem.

# **Description of the Tool** 
The tool is a Python-based OpenBIM ifcOpenShell solution designed to calculate the total window area for two ifc files and comparing the two files.
It shows the total area of two ifc files. Preferably two renovation files. One showing the old building and one showing the new version of said building. By comparing the two files it would therefore be able to show the total area of new implemented windows and the total window area of the two files.
This can be used to make an easy LCA of the windows for the renovated building by implementing EPD's for the windows and multiplying with the desired impact category.

# **Instructions to Run the Tool**
## **1. Input Data**
Import two IFC files, one containing the old building and one containing the renovated version of said building.

## **2. Run Script**
Execute the Python script to calculate the total window area.

## **3. Analyze Results**
Compare results for both of the files.

## **4. Output**
Generate area of total window area and dimensions for every window in the model. Here's how it would look: 

--- OLD BUILDING ---


TOTAL RESULTS \
Windows: 229 \
Successful calculations: 172 \
Geometry errors: 57 \
Total window area: 329.537 m2 

WINDOW DIMENSION SUMMARY \
2 windows | 3.075 x 1.012 x 0.140 m | Area per window: 3.112 m2 \
3 windows | 3.075 x 1.011 x 0.140 m | Area per window: 3.109 m2 \
1 windows | 3.075 x 0.984 x 0.140 m | Area per window: 3.026 m2 \
3 windows | 2.940 x 2.900 x 0.115 m | Area per window: 8.526 m2 \
1 windows | 2.275 x 1.024 x 0.140 m | Area per window: 2.330 m2\
50 windows | 2.275 x 1.012 x 0.140 m | Area per window: 2.302 m2\
2 windows | 2.225 x 1.024 x 0.140 m | Area per window: 2.278 m2 \
1 windows | 2.225 x 1.023 x 0.140 m | Area per window: 2.276 m2\
1 windows | 2.225 x 1.022 x 0.140 m | Area per window: 2.274 m2\
51 windows | 2.225 x 1.012 x 0.140 m | Area per window: 2.252 m2\
3 windows | 2.225 x 1.011 x 0.140 m | Area per window: 2.249 m2\
2 windows | 2.225 x 1.001 x 0.140 m | Area per window: 2.227 m2\
1 windows | 2.172 x 1.024 x 0.140 m | Area per window: 2.224 m2\
36 windows | 2.100 x 0.220 x 0.115 m | Area per window: 0.462 m2\
4 windows | 1.292 x 1.027 x 0.140 m | Area per window: 1.327 m2\
1 windows | 1.292 x 1.024 x 0.140 m | Area per window: 1.323 m2\
1 windows | 1.292 x 1.012 x 0.140 m | Area per window: 1.308 m2\
2 windows | 1.247 x 0.841 x 0.140 m | Area per window: 1.049 m2\
1 windows | 1.247 x 0.441 x 0.140 m | Area per window: 0.550 m2\
1 windows | 1.247 x 0.300 x 0.140 m | Area per window: 0.374 m2\
1 windows | 1.247 x 0.167 x 0.140 m | Area per window: 0.208 m2\
1 windows | 1.247 x 0.140 x 0.041 m | Area per window: 0.175 m2\
3 windows | 1.012 x 0.875 x 0.140 m | Area per window: 0.885 m2\
\
--- NEW BUILDING ---

TOTAL RESULTS\
Windows: 117\
Successful calculations: 117\
Geometry errors: 0\
Total window area: 613.664 m2

WINDOW DIMENSION SUMMARY\
100 windows | 3.200 x 1.800 x 0.150 m | Area per window: 5.760 m2\
3 windows | 2.110 x 1.050 x 0.313 m | Area per window: 2.216 m2\
14 windows | 2.110 x 1.050 x 0.193 m | Area per window: 2.216 m2

--- COMPARISON ---\
Old window area: 329.537 m2\
New window area: 613.664 m2\
Difference: 284.126 m2 \
PS C:\Users\augus\AppData\Local\Programs\Microsoft VS Code> 

# **Video tutorial**
This tutorial goes more in depth as to what the script shows and how it runs.

INSERT MP4 file



# **Subjects That Might Use the Tool:**
- LCA
- LCC
- MEP
- Architect

# **Required Information for the Tool:**
- ifc file for old building
- ifc file for new building
- Newest version of ifcOpenShell
