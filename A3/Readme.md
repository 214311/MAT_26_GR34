# **Problem/Claim**
The tool addresses the challenge that comes when trying to do a comparison of Windows from an old model compared to a new model of that same building.
Used especially in renovation.    

# **Source of the Problem**
The main problem occurred when looking through old LCA reports of renovation projects of the building 308 at DTU-Lyngby done through the course "Advanced buildingdesign". It was easy to make an script returning the total square meter of windows used. The main difficulty was to get it to show the newly implemented windows. This has been done by comparing an ifc file of the old building with an ifc file of the new building. 
By running this script it shows the difference in window area between the two files and therefore solves this problem.

# **Description of the Tool** 
The tool is a Python-based OpenBIM ifcOpenShell solution designed to calculate the total window area for two ifc files and comparing the two files.
It shows the total area of two ifc files. Preferably two renovation files. One showing the old building and one showing the new building. By comparing the two files it would therefore be able to show how many square meter of new window have been added and how many square meter window both of the files have in total.
This can be used to make an easy LCA of the windows for the renovated building by implementing EPD's for the windows and multiplying with the desired impact category.

# **Instructions to Run the Tool**
## **1. Input Data**
Import two IFC files, one containing the old building and one containing the renovated version of said building.

## **2. Run Script**
Execute the Python script to calculate the total window area.

## **3. Analyze Results**
Compare results for both of the files.

## **4. Output**
Generate area of total window area.

# **Video tutorial**
This tutorial goes more in depth as to what the script shows and how it runs.

# **Subjects That Might Use the Tool:**
- LCA
- LCC
- MEP
- Architect

# **Required Information for the Tool:**
- ifc file for old building
- ifc file for new building
- Newest version of OpenShell
