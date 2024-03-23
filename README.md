Follow the steps to re-use STIG Simulator in your environment (Recommended: PyCharm tool)
================================================
Installation Video Guide: Zenodo Repository

Prerequisites:
Install Pycharm Tool to run the artifact. 
Use the following link: 

Windows: https://www.jetbrains.com/pycharm/download/?section=windows

macOS:   https://www.jetbrains.com/pycharm/download/?section=mac

================================================

For Default Interference Scenario: (Tea Shop, Book Shop, & Sock Shop)
1.	Configure the Environment:
•	Clone the STIG_Simulator project into the PyCharm tool.
2.	Install Dependencies:
•	Execute pip install -r requirements.txt in the terminal.
3.	Run the temporal_graph.py File:
•	This file inputs graphs to the simulator and generates temporal call graphs for a specified host (e.g., worker_1). As a result, you can see Knowledge deployment graphs, distinct paths, and Host_service relation graphs that are used for temporal graph generation. Ground truth for selected host (e,g. worker_1) is generated that contains possible sources and targets of interference effects.
4.	Run the STIG_generation.py File to Generate STIGs:
•	Use default settings: This file uses generated temporal graphs and ground truth to generate a number of ranked STIGs (Spatio-Temporal Interference Graphs). The main file, STIG_generation, calls other files to produce STIGs.

Evaluation of generated STIGs: 
1.	Figure 4 shows a structural dependency matrix (SDM ) representing the interference probabilities (STIG edges) between source and target services (STIG nodes) of SockShop and TeaShop, where the darker colors represent higher probability. For more details, follow section 4.1 STIG Analysis in artifact paper. 
2.	Table 1 is calculated from the data provided from traces of bookshop and teashop (Location: STIGS-Artifact/data/traces and a complete detailed formulas to calculate Probability of Necessity (PN) and Probability of Sufficiency (PS) are present in excel_filtered_combined_services_anomalies.xlsx file. For more details, follow section 4.2 Reconfiguration Plan in artifact paper. 

	
================================================

Customize Scenario

1.	Configure the Environment (Repeat):
•	Clone the STIG_Simulator project into the PyCharm tool.
2.	Install Dependencies (Repeat):
•	Execute pip install -r requirements.txt in the terminal.
3.	Customize temporal_graph.py File:
•	The file contains input graphs for the simulator and generates temporal call graphs for a specified host (e.g., worker_1).
(a) In the temporal_graph.py file, initially customize the system architecture and deployment configuration file and choose a path where you want to store the generated temporal call graph.
  	
         Example: knowledge_graph = knowledge_graph_utils.get_knowledge_graph('data/input_graphs/System_Architecture.xml','data/input_graphs/Deployment_Config.yaml').

  	 System_Architecture.xml is based on the call graph of each shop and placement of services in the particular host in Kubernetes cluster
  	
         File path: file_path = 'data/callgraph_generator/temporal_callgraph_W1.npy'.
  	 For each worker, temporal_callgraph_WX would be different and should generated and stored in memory first then called by algorithm that is explained in next (3b)

(b) Choose a worker node to generate "Source (query) and Target (predicate) stack of Interference."
 
        Example: query_predicate_stacks = generate_query_predicate_stacks(knowledge_graph, 'worker1', file_path)
	
4.	Run the STIG_generation.py with Custom Settings:

Before running, change SOURCE_NODE = 'A1', TARGET_NODE = 'B1' according to new ground truth values (visible in debugging mode in temporal_graph.py). For each worker node, ground truth will be changed accordingly and you can choose any ground truth pair by debugging temporal_graph.py file 

Note: In STIG_generation.py, set NUMBER_OF_MODELS = 2 (up to 10 rankings of STIGs can be generated using graph embedding metrics found in the Metrics Folder). Set VISUALIZE = True to enable visualization, though note that enabling visualization will make the first ranking very costly but will print all the STIGs.



	


      
