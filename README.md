
Follow the steps to re-use STIG Simulator in your environment (Recommended: PyCharm tool)
================================================
Installation Video Guide: https://youtu.be/JUV-zH51l0Y

Prerequisites:

Install Pycharm Tool to run the artifact. 
Use the following link: 
for Windows: https://www.jetbrains.com/pycharm/download/?section=windows
for macOS:   https://www.jetbrains.com/pycharm/download/?section=mac


	 For Default Interference Scenario: {Tea Shop & Book Shop & Sock Shop} 

Step:1 Configure the Environment (Clone the STIG_Simulator project into Pycharm tool)

Step 2: pip install -r requirements.txt (using terminal) 

Step 3: Run the temporal_graph.py file 
	(it contains input graphs to simulator and generate temporal call graphs for specified host (e.g worker_1), as a result you can see Knowledghe deployment graphs, distinct paths and 	Host_service relation graph that is used for temporal graph generation). Ground truth is generated that contains possible source and target of interference effect. 

Step 4: Run the STIG_generation.py file to see Generated STIGs. (Interference Graphs)(Use default settings)
       This file use generated temporal graphs and ground truth and generate no.of ranked stigs. 
       
Note:  Main file is STIG_generation that is calling other files to product STIGs(Spatio-Temporal Interference Graphs)


         Customize Scenario:

Step: 1  Step:1 Configure the Environment (Clone the STIG_Simulator project into Pycharm tool)

Step 2: pip install -r requirements.txt (using terminal)

Step 3: temporal_graph.py file contains input graphs to simulator and generate temporal call graphs for specified host (e.g worker_1) 
   	(a) In temporal_graph.py file, initial customized system architecture and deployment configuration file  
            and choose a path where you want to store generated temporal call graph. 
        Code line 12: 
                def main():

    	 knowledge_graph = knowledge_graph_utils.get_knowledge_graph('data/input_graphs/System_Architecture.xml','data/input_graphs/Deployment_Config.yaml')
    	 file_path = 'data/callgraph_generator/temporal_callgraph_W1.npy'
------
        (b) code line 33: Choose worker node to generate "Source(query) and Target(predicate) stack of Interference "
                           query_predicate_stacks = generate_query_predicate_stacks(knowledge_graph, 'worker1', file_path)

Step 4: Run the STIG_generation.py 
  Before running :
change  SOURCE_NODE = 'A1' , TARGET_NODE = 'B1' ( According to new ground truth values, you can see ground truth values in debugging mode) -> (In temporal_graph.py)

****Note**** (Code line: 202, STIG_generation.py )
NUMBER_OF_MODELS = 2 (up to 10 rankings of STIGs can generate using graph embedding metrics (Metrics Folder))
VISUALIZE = True  # Enabling visualization will make first ranking very costly but print all the STIGs

